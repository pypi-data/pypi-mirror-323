import copy
import time
from abc import ABC, abstractmethod

from autowsgr.constants import literals
from autowsgr.constants.custom_exceptions import ImageNotFoundErr, NetworkErr
from autowsgr.constants.image_templates import IMG
from autowsgr.constants.other_constants import ALL_SHIP_TYPES, SAP
from autowsgr.constants.positions import BLOOD_BAR_POSITION
from autowsgr.constants.ui import Node
from autowsgr.game.expedition import Expedition
from autowsgr.game.game_operation import (
    click_result,
    destroy_ship,
    detect_ship_stats,
    get_ship,
    match_night,
)
from autowsgr.game.get_game_info import get_enemy_condition
from autowsgr.timer import Timer
from autowsgr.utils.io import recursive_dict_update, yaml_to_dict
from autowsgr.utils.math_functions import get_nearest


def start_march(timer: Timer, position=(900, 500)):
    timer.click(*position, 1, delay=0)
    start_time = time.time()
    while timer.identify_page('fight_prepare_page'):
        if time.time() - start_time > 3:
            timer.click(*position, 1, delay=0)
            time.sleep(1)
        if timer.image_exist(IMG.symbol_image[3], need_screen_shot=0):
            return literals.DOCK_FULL_FLAG
        if timer.image_exist(IMG.symbol_image[9], need_screen_shot=0, confidence=0.8):
            time.sleep(1)
            return literals.BATTLE_TIMES_EXCEED
        if time.time() - start_time > 15:
            if timer.process_bad_network():
                if timer.identify_page('fight_prepare_page'):
                    return start_march(timer, position)
                NetworkErr('stats unknown')
            else:
                raise TimeoutError('map_fight prepare timeout')
    return literals.OPERATION_SUCCESS_FLAG


class FightResultInfo:
    def __init__(self, timer: Timer, ship_stats) -> None:
        try:
            mvp_pos = timer.wait_image(IMG.fight_image[14])
            self.mvp = get_nearest((mvp_pos[0], mvp_pos[1] + 20), BLOOD_BAR_POSITION[1])
        except Exception as e:
            timer.log_screen(name='mvp_image')
            timer.logger.warning(f"can't identify mvp, error: {e}")
        self.ship_stats = detect_ship_stats(timer, 'sumup', ship_stats)

        self.result = timer.wait_images(IMG.fight_result, timeout=5)
        if timer.image_exist(IMG.fight_result['SS'], need_screen_shot=False):
            self.result = 'SS'
        if self.result is None:
            timer.log_screen()
            timer.logger.warning("can't identify fight result, screen logged")

    def __str__(self) -> str:
        return f'MVP 为 {self.mvp} 号位, 战果为 {self.result}'

    def __lt__(self, other) -> bool:  # <
        order = ['D', 'C', 'B', 'A', 'S', 'SS']
        if isinstance(other, FightResultInfo):
            other = other.result

        return order.index(self.result) < order.index(other)

    def __le__(self, other) -> bool:  # <=
        order = ['D', 'C', 'B', 'A', 'S', 'SS']
        if isinstance(other, FightResultInfo):
            other = other.result

        return order.index(self.result) <= order.index(other)

    def __gt__(self, other) -> bool:  # >
        return not (self <= other)

    def __ge__(self, other) -> bool:  # >=
        return not (self < other)


class FightEvent:
    """战斗事件类
    事件列表: 战况选择, 获取资源, 索敌成功, 迂回, 阵型选择, 进入战斗, 是否夜战, 战斗结算, 获取舰船, 继续前进, 自动回港

    状态: 一个字典, 一共三种键值
        position: 位置, 所有事件均存在

        ship_stats: 我方舰船状态(仅在 "继续前进" 事件存在)

        enemys: 敌方舰船(仅在 "索敌成功" 事件存在), 字典或 "索敌失败"

        info: 其它额外信息(仅在 "自动回港" 事件存在)

    动作: 一个字符串
        "继续": 获取资源, 迂回, 战斗结算, 获取舰船, 自动回港等不需要决策的操作

        数字字符串: 战况选择的决策

        "SL"/数字字符串: 阵型选择的决策

        "继续"/ "SL": 进入战斗后的决策

        "战斗"/"撤退"/"迂回": 索敌成功的决策

        "追击"/"撤退": 夜战的决策

        "回港/前进": 是否前进的选择(战斗结算完毕后)

    结果: 一个字符串
        "无": 战况选择, 获取资源, 索敌成功, 阵型选择, 进入战斗, 是否夜战, 继续前进, 自动回港,

        (FightResultInfo): 表示战果信息, 战果结算

        舰船名: 获取舰船
    """

    def __init__(self, event, stats, action='继续', result='无') -> None:
        self.event = event
        self.stats = stats
        self.action = action
        self.result = result

    def __str__(self) -> str:
        return f'事件:{self.event}, 状态:{self.stats}, 动作:{self.action}, 结果:{self.result!s}'

    def __repr__(self) -> str:
        return f'FightEvent({self.event}, {self.stats}, {self.action}, {self.result})'


class FightHistory:
    """记录并处理战斗历史信息"""

    def __init__(self) -> None:
        self.events = []

    def add_event(self, event, point, action='继续', result='无'):
        self.events.append(FightEvent(event, point, action, result))

    def reset(self):
        self.events = []

    def get_fight_results(self):
        results_dict = {}
        results_list = []
        for event in self.events:
            if event.event == '战果结算':
                if event.stats['position'].isalpha():
                    results_dict[event.stats['position']] = event.result
                else:
                    results_list.append(event.result)
        return results_list if len(results_list) else results_dict

    def get_last_point(self):
        return self.events[-1].stats['position']

    def __str__(self) -> str:
        return ''.join(str(event) + '\n' for event in self.events)


class FightInfo(ABC):
    """存储战斗中需要用到的所有状态信息, 以及更新逻辑"""

    def __init__(self, timer: Timer) -> None:
        self.timer = timer
        self.config = timer.config
        self.logger = timer.logger

        self.successor_states = {}  # 战斗流程的有向图建模，在不同动作有不同后继时才记录动作
        self.state2image = {}  # 所需用到的图片模板。格式为 [模板，等待时间]
        self.after_match_delay = {}  # 匹配成功后的延时。格式为 {状态名 : 延时时间(s),}
        self.last_state = ''
        self.last_action = ''
        self.state = ''
        self.enemys = {}  # 敌方舰船列表
        self.ship_stats = []  # 我方舰船血量列表
        self.oil = 10  # 我方剩余油量
        self.ammo = 10  # 我方剩余弹药量
        self.fight_history = FightHistory()  # 战斗结果记录

    def update_state(self):
        self.last_state = self.state

        # 计算当前可能的状态
        possible_states = copy.deepcopy(self.successor_states[self.last_state])
        if isinstance(possible_states, dict):
            possible_states = possible_states[self.last_action]
        modified_timeout = [-1 for _ in possible_states]  # 某些状态需要修改等待时间
        for i, state in enumerate(possible_states):
            if isinstance(state, list):
                state, timeout = state
                possible_states[i] = state
                modified_timeout[i] = timeout
        if self.config.show_match_fight_stage:
            self.logger.debug('waiting:', possible_states, '  ')
        images = [self.state2image[state][0] for state in possible_states]
        timeout = [self.state2image[state][1] for state in possible_states]
        confidence = min(
            [0.8]
            + [
                self.state2image[state][2]
                for state in possible_states
                if len(self.state2image[state]) >= 3
            ],
        )
        timeout = [
            timeout[i] if modified_timeout[i] == -1 else modified_timeout[i]
            for i in range(len(timeout))
        ]
        timeout = max(timeout)
        # 等待其中一种出现
        fun_start_time = time.time()
        while time.time() - fun_start_time <= timeout:
            self._before_match()

            # 尝试匹配
            ret = [self.timer.image_exist(image, False, confidence=confidence) for image in images]
            if any(ret):
                self.state = possible_states[ret.index(True)]
                # 查询是否有匹配后延时
                if self.state in self.after_match_delay:
                    delay = self.after_match_delay[self.state]
                    time.sleep(delay)

                if self.config.show_match_fight_stage:
                    self.logger.info(f'matched: {self.state}')
                self._after_match()

                return self.state

        # 匹配不到时报错
        self.logger.warning(
            f'匹配状态失败! state: {self.state}  last_action: {self.last_action}',
        )
        self.timer.log_screen(True)
        for image in images:
            self.logger.log_image(image, f'match_{time.time()!s}.PNG')
        raise ImageNotFoundErr

    @abstractmethod
    def _before_match(self):
        """每一轮尝试匹配状态前执行的操作"""

    def _after_match(self):
        """匹配到状态后执行的操作"""
        if self.state == 'spot_enemy_success':
            self.enemys = get_enemy_condition(self.timer, 'fight')
        if self.state == 'result':
            try:
                result = FightResultInfo(self.timer, self.ship_stats)
                self.ship_stats = result.ship_stats
                self.fight_history.add_event(
                    '战果结算',
                    {
                        'position': (
                            self.node
                            if 'node' in self.__dict__
                            else f'此类战斗({type(self)})不支持节点信息'
                        ),
                    },
                    result=result,
                )
            except Exception as e:
                self.logger.warning(f'战果结算记录失败：{e}')

    @abstractmethod
    def reset(self):
        """需要记录与初始化的战斗信息"""


class FightPlan(ABC):
    def __init__(self, timer: Timer) -> None:
        # 把 timer 引用作为内置对象，减少函数调用的时候所需传入的参数
        self.timer = timer
        self.config = timer.config
        self.logger = timer.logger
        self.fight_logs = []

    def fight(self):
        self.info.reset()  # 初始化战斗信息
        while True:
            ret = self._make_decision()
            if ret == literals.FIGHT_CONTINUE_FLAG:
                continue
            if ret == 'need SL':
                self._sl()
                return 'SL'
            if ret == literals.FIGHT_END_FLAG:
                self.timer.set_page(self.info.end_page)
                self.fight_logs.append(self.info.fight_history)
                return 'success'

    def run_for_times(self, times, gap=1800):
        """多次执行同一任务, 自动进行远征操作
        Args:
            times (int): 任务执行总次数

            gap (int): 强制远征检查的间隔时间
        Raise:
            RuntimeError: 战斗进行时出现错误
        Returns:
            str:
                "OK": 任务正常结束

                "dock is full" 因为船坞已满并且没有设置解装因此退出任务
        """
        assert times >= 1
        expedition = Expedition(self.timer)
        for i in range(times):
            if time.time() - self.timer.last_expedition_check_time >= gap:
                expedition.run(True)
            elif isinstance(self.timer.now_page, Node) and self.timer.now_page.name == 'map_page':
                expedition.run(False)
                self.timer.goto_game_page('map_page')
            fight_flag = self.run()
            if fight_flag not in ['SL', 'success']:
                if fight_flag == 'dock is full':
                    return 'dock is full'
                if fight_flag == literals.SKIP_FIGHT:
                    return literals.SKIP_FIGHT
                raise RuntimeError(f'战斗进行时出现异常, 信息为 {fight_flag}')
            self.timer.logger.info(f'已出击次数:{i+1}，目标次数{times}')
        return 'OK'

    def run(self):
        """主函数，负责一次完整的战斗.
        Returns:
            str:
                'dock is full': 船坞已满并且没有设置自动解装

                'fight end': 战斗结束标志, 一般不返回这个, 和 success 相同

                'out of times': 战斗超时

                'SL': 进行了 SL 操作

                'success': 战斗流程正常结束(到达了某个结束点或者选择了回港)

        """
        # 战斗前逻辑
        ret = self._enter_fight()

        if ret == literals.OPERATION_SUCCESS_FLAG:
            pass
        elif ret == literals.DOCK_FULL_FLAG:
            # 自动解装功能
            if self.config.dock_full_destroy:
                self.timer.relative_click(0.38, 0.565)
                destroy_ship(self.timer)
                return self.run()
            return ret
        elif ret == literals.FIGHT_END_FLAG:
            self.timer.set_page(self.info.end_page)
            return ret
        elif ret == literals.BATTLE_TIMES_EXCEED or ret == literals.SKIP_FIGHT:
            return ret
        else:
            self.logger.error('无法进入战斗, 原因未知! 屏幕状态已记录')
            self.timer.log_screen()
            raise BaseException(str(time.time()) + 'enter fight error')

        # 战斗中逻辑
        return self.fight()

    def run_for_times_condition(self, times, last_point, result='S', insist_time=900):
        """有战果要求的多次运行, 使用前务必检查参数是否有误, 防止死循环

        Args:
            times: 次数

            last_point: 最后一个点

            result: 战果要求

            insist_time: 如果大于这个时间工作量未减少则退出工作

        Returns:
            str:
                "OK": 任务顺利结束

                "dock is full": 因为船坞已满并且不允许解装所以停止
        """
        if not isinstance(result, str) or not isinstance(last_point, str):
            raise TypeError(
                f'last_point, result must be str,but is {type(last_point)}, {type(result)}',
            )
        if result not in ['S', 'A', 'B', 'C', 'D', 'SS']:
            raise ValueError(
                f"result value {result} is illegal, it should be 'A','B','C','D','S' or 'SS'",
            )
        if len(last_point) != 1 or ord(last_point) > ord('Z') or ord(last_point) < ord('A'):
            raise ValueError("last_point should be a uppercase within 'A' to 'Z'")
        import time

        result_list = ['SS', 'S', 'A', 'B', 'C', 'D']
        start_time = time.time()
        while times:
            ret = self.run()
            if ret == 'dock is full':
                self.timer.logger.error('船坞已满, 无法继续')
                return ret

            self.logger.info('战斗信息:\n' + str(self.info.fight_history))
            fight_results = sorted(self.info.fight_history.get_fight_results().items())
            # 根据情况截取战果，并在result_list查找索引
            if len(fight_results):
                if str(fight_results[-1][1])[-2].isalpha():
                    fight_result_index = result_list.index(
                        str(fight_results[-1][1])[-2:],
                    )
                else:
                    fight_result_index = result_list.index(
                        str(fight_results[-1][1])[-1],
                    )

            finish = (
                len(fight_results)
                and fight_results[-1][0] == last_point
                and fight_result_index <= result_list.index(result)
            )
            if not finish:
                self.timer.logger.info(
                    f'不满足预设条件, 此次战斗不计入次数, 剩余战斗次数:{times}',
                )
                if time.time() - start_time > insist_time:
                    return False
            else:
                start_time, times = time.time(), times - 1
                self.timer.logger.info(
                    f'完成了一次满足预设条件的战斗, 剩余战斗次数:{times}',
                )
        return 'OK'

    def update_state(self, *args, **kwargs):
        try:
            self.info.update_state()
            state = self.info.state
            self.timer.keep_try_update_fight = 0
        except ImageNotFoundErr as _:
            # 处理点击延迟或者网络波动导致的匹配失败
            if (
                hasattr(self.timer, 'keep_try_update_fight')
                and self.timer.keep_try_update_fight > 3
            ):
                return 'need_SL'
            if hasattr(self.timer, 'keep_try_update_fight'):
                self.timer.keep_try_update_fight += 1
            else:
                self.timer.keep_try_update_fight = 1
            self.logger.warning('Image Match Failed, Trying to Process')
            if self.timer.is_other_device_login():
                self.timer.process_other_device_login()  # TODO: 处理其他设备登录
            if self.timer.is_bad_network(timeout=5):
                self.timer.process_bad_network(extra_info='update_state', timeout=5)
            self._make_decision(skip_update=True)
            # if self.info.last_state == "spot_enemy_success":
            #     if self.timer.image_exist(IMG.fight_image[2]):
            #         self.timer.click(900, 500)
            # if self.info.last_state in ["proceed", "night"] and self.timer.image_exist(
            #     IMG.fight_image[5:7]
            # ):
            #     if self.info.last_action == "yes":
            #         self.timer.click(325, 350, times=1)
            #     else:
            #         self.timer.click(615, 350, times=1)

            if 'try_times' not in kwargs:
                return self.update_state(try_times=1)
            time.sleep(10 * 2.5 ** kwargs['try_times'])
            return self.update_state(try_times=kwargs['try_times'] + 1)
        return state

    @abstractmethod
    def _enter_fight(self) -> str:
        pass

    @abstractmethod
    def _make_decision(self, *args, **kwargs) -> str:
        pass

    # =============== 战斗中通用的操作 ===============
    def _sl(self):
        self.timer.logger.debug('正在执行SL操作')
        # 重置地图节点信息
        self.timer.reset_chapter_map()

        self.timer.restart()
        self.timer.go_main_page()
        self.timer.set_page('main_page')


class DecisionBlock:
    """地图上一个节点的决策模块"""

    def __init__(self, timer: Timer, args) -> None:
        self.timer = timer
        self.config = timer.config
        self.logger = timer.logger

        self.__dict__.update(args)

        # 用于根据规则设置阵型
        self.set_formation_by_rule = False
        self.formation_by_rule = 0

    def _check_rules(self, enemys: dict):
        for rule in self.enemy_rules:
            condition, act = rule
            rcondition = ''
            last = 0
            for i, ch in enumerate(condition):
                if ord(ch) > ord('Z') or ord(ch) < ord('A'):
                    if last != i:
                        if condition[last:i] in ALL_SHIP_TYPES:
                            rcondition += f"enemys.get('{condition[last:i]}', 0)"
                        else:
                            rcondition += condition[last:i]
                    rcondition += ch
                    last = i + 1

            if self.config.show_enemy_rules:
                self.logger.info(rcondition)
            if eval(rcondition):
                return act
        return None

    def make_decision(self, state, last_state, last_action, info: FightInfo):
        # destroy_ship skip: extract-method
        """单个节点的决策"""
        enemys = info.enemys
        if state in ['fight_period', 'night_fight_period']:
            if self.SL_when_enter_fight:
                info.fight_history.add_event(
                    '进入战斗',
                    {
                        'position': (
                            info.node
                            if 'node' in info.__dict__
                            else f'此类战斗({type(info)})不包含节点信息'
                        ),
                    },
                    'SL',
                )
                return None, 'need SL'
            return None, literals.FIGHT_CONTINUE_FLAG

        if state == 'spot_enemy_success':
            retreat = (
                self.supply_ship_mode == 1 and enemys.get(SAP, 0) == 0
            )  # 功能: 遇到补给舰则战斗，否则撤退
            can_detour = self.timer.image_exist(
                IMG.fight_image[13],
            )  # 判断该点是否可以迂回
            detour = can_detour and self.detour  # 由 Node 指定是否要迂回

            # 功能, 根据敌方阵容进行选择
            act = self._check_rules(enemys=enemys)

            if act == 'retreat':
                retreat = True
            elif act == 'detour':
                try:
                    assert can_detour, '该点无法迂回, 但是规则中指定了迂回'
                except AssertionError:
                    raise ValueError('该点无法迂回, 但在规则中指定了迂回')
                detour = True
            elif isinstance(act, int):
                self.set_formation_by_rule = True
                self.formation_by_rule = act

            if retreat:
                self.timer.click(677, 492, delay=0.2)
                info.fight_history.add_event(
                    '索敌成功',
                    {
                        'position': (
                            info.node
                            if 'node' in info.__dict__
                            else f'此类战斗({type(info)})不包含节点信息'
                        ),
                    },
                    '撤退',
                )
                return 'retreat', literals.FIGHT_END_FLAG
            if detour:
                image_detour = IMG.fight_image[13]
                if self.timer.click_image(image=image_detour, timeout=2.5):
                    self.timer.logger.info('成功执行迂回操作')
                else:
                    self.timer.logger.error('未找到迂回按钮')
                    self.timer.log_screen(True)
                    raise ImageNotFoundErr("can't found image")

                # self.timer.click(540, 500, delay=0.2)
                info.fight_history.add_event(
                    '索敌成功',
                    {
                        'position': (
                            info.node
                            if 'node' in info.__dict__
                            else f'此类战斗({type(info)})不包含节点信息'
                        ),
                    },
                    '迂回',
                )
                return 'detour', literals.FIGHT_CONTINUE_FLAG

            info.fight_history.add_event(
                '索敌成功',
                {
                    'position': (
                        info.node
                        if 'node' in info.__dict__
                        else f'此类战斗({type(info)})不包含节点信息'
                    ),
                },
                '战斗',
            )
            if self.long_missile_support:
                image_missile_support = IMG.fight_image[17]
                if self.timer.click_image(image=image_missile_support, timeout=2.5):
                    self.timer.logger.info('成功开启远程导弹支援')
                else:
                    self.timer.logger.error('未找到远程支援按钮')
                    raise ImageNotFoundErr("can't found image of long_missile_support")
            self.timer.click(855, 501, delay=0.2)
            # self.timer.click(380, 520, times=2, delay=0.2) # TODO: 跳过可能的开幕支援动画，实现有问题
            return 'fight', literals.FIGHT_CONTINUE_FLAG
        if state == 'formation':
            spot_enemy = last_state == 'spot_enemy_success'
            value = self.formation
            if spot_enemy:
                if self.SL_when_detour_fails and last_action == 'detour':
                    info.fight_history.add_event(
                        '迂回',
                        {
                            'position': (
                                info.node
                                if 'node' in info.__dict__
                                else f'此类战斗({type(info)})不包含节点信息'
                            ),
                        },
                        result='失败',
                    )
                    info.fight_history.add_event(
                        '阵型选择',
                        {
                            'enemys': enemys,
                            'position': (
                                info.node
                                if 'node' in info.__dict__
                                else f'此类战斗({type(info)})不包含节点信息'
                            ),
                        },
                        action='SL',
                    )
                    return None, 'need SL'

                if self.set_formation_by_rule:
                    self.logger.debug('set formation by rule:', self.formation_by_rule)
                    value = self.formation_by_rule
                    self.set_formation_by_rule = False
            else:
                if self.SL_when_spot_enemy_fails:
                    info.fight_history.add_event(
                        '阵型选择',
                        {
                            'enemys': '索敌失败',
                            'position': (
                                info.node
                                if 'node' in info.__dict__
                                else f'此类战斗({type(info)})不包含节点信息'
                            ),
                        },
                        action='SL',
                    )
                    return None, 'need SL'
                if self.formation_when_spot_enemy_fails:
                    value = self.formation_when_spot_enemy_fails
            info.fight_history.add_event(
                '阵型选择',
                {
                    'enemys': (enemys if last_state == 'spot_enemy_success' else '索敌失败'),
                    'position': (
                        info.node
                        if 'node' in info.__dict__
                        else f'此类战斗({type(info)})不包含节点信息'
                    ),
                },
                action=value,
            )
            # import random
            # if random.random() > 0.5:
            #     print("这次没点起")
            # else:
            #     self.timer.click(573, value * 100 - 20, delay=2)
            self.timer.click(573, value * 100 - 20, delay=2)
            return value, literals.FIGHT_CONTINUE_FLAG
        if state == 'night':
            is_night = self.night
            info.fight_history.add_event(
                '是否夜战',
                {
                    'position': (
                        info.node
                        if 'node' in info.__dict__
                        else f'此类战斗({type(info)})不包含节点信息'
                    ),
                },
                action='追击' if is_night else '撤退',
            )

            match_night(self.timer, is_night)
            if is_night:
                # self.timer.click(325, 350)
                return 'yes', literals.FIGHT_CONTINUE_FLAG
            # self.timer.click(615, 350)
            return 'no', literals.FIGHT_CONTINUE_FLAG

        if state == 'result':
            # time.sleep(1.5)
            # self.timer.click(900, 500, times=2, delay=0.2)
            click_result(self.timer)
            return None, literals.FIGHT_CONTINUE_FLAG
        if state == 'get_ship':
            get_ship(self.timer)
            return None, literals.FIGHT_CONTINUE_FLAG
        self.logger.error('Unknown State')
        raise BaseException


class IndependentFightPlan(FightPlan):
    def __init__(
        self,
        timer: Timer,
        end_image,
        plan_path=None,
        *args,
        **kwargs,
    ) -> None:
        """创建一个独立战斗模块, 处理从形如战役点击出征到收获舰船(或战果结算)的整个过程
        Args:
            end_image (MyTemplate): 整个战斗流程结束后的图片
        """
        super().__init__(timer)
        default_args = yaml_to_dict(self.timer.plan_tree['default'])
        node_defaults = default_args['node_defaults']
        node_args = yaml_to_dict(plan_path) if (plan_path is not None) else kwargs
        node_args = recursive_dict_update(node_defaults, node_args)
        self.decision_block = DecisionBlock(timer, node_args)
        self.info = IndependentFightInfo(timer, end_image)

    def run(self):
        super().fight()

    def _make_decision(self, *args, **kwargs):
        if 'skip_update' not in kwargs:
            state = self.update_state()
        if self.info.state == 'battle_page':
            return literals.FIGHT_END_FLAG
        if state == 'need SL':
            return 'need SL'

        # 进行通用NodeLevel决策
        action, fight_stage = self.decision_block.make_decision(
            self.info.state,
            self.info.last_state,
            self.info.last_action,
            self.info,
        )
        self.info.last_action = action
        return fight_stage


class IndependentFightInfo(FightInfo):
    def __init__(self, timer: Timer, end_image) -> None:
        super().__init__(timer)

        self.end_page = 'battle_page'

        self.successor_states = {
            'proceed': ['spot_enemy_success', 'formation', 'fight_period'],
            'spot_enemy_success': {
                'retreat': ['battle_page'],
                'fight': ['formation', 'fight_period'],
            },
            'formation': ['fight_period'],
            'fight_period': ['night', 'result'],
            'night': {
                'yes': ['night_fight_period'],
                'no': [['result', 8]],
            },
            'night_fight_period': ['result'],
            'result': ['battle_page'],  # 两页战果
        }

        self.state2image = {
            'proceed': [IMG.fight_image[5], 5],
            'spot_enemy_success': [IMG.fight_image[2], 15],
            'formation': [IMG.fight_image[1], 15],
            'fight_period': [IMG.symbol_image[4], 3],
            'night': [IMG.fight_image[6], 120],
            'night_fight_period': [IMG.symbol_image[4], 3],
            'result': [IMG.fight_image[16], 60],
            'battle_page': [end_image, 5],
        }

    def reset(self):
        self.last_state = ''
        self.last_action = ''
        self.state = 'proceed'

    def _before_match(self):
        # 点击加速
        if self.state in ['proceed']:
            self.timer.click(
                380,
                520,
                delay=0,
                enable_subprocess=True,
            )
        self.timer.update_screen()

    def _after_match(self):
        pass  # 战役的敌方信息固定，不用获取
