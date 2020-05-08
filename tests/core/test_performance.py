from dataclasses import dataclass
from timeit import timeit
from typing import Optional, Sequence

from dacite import from_dict, Config


def test_performance():
    @dataclass(frozen=True)
    class Statistic:
        stat_type: str
        category: Optional[str]
        ast_sack: Optional[int]
        ast_tackle: Optional[int]
        att_yards: Optional[int]
        attempt: Optional[int]
        batted_pass: Optional[int]
        blitz: Optional[int]
        broken_tackles: Optional[int]
        catchable: Optional[int]
        complete: Optional[int]
        def_comp: Optional[int]
        def_target: Optional[int]
        description: Optional[str]
        down: Optional[int]
        downed: Optional[int]
        dropped: Optional[int]
        endzone: Optional[int]
        faircatch: Optional[int]
        firstdown: Optional[int]
        forced: Optional[int]
        forced_fumble: Optional[int]
        fumble: Optional[int]
        goaltogo: Optional[int]
        gross_yards: Optional[int]
        hang_time: Optional[float]
        hurry: Optional[int]
        incompletion_type: Optional[str]
        inside_20: Optional[int]
        int_yards: Optional[float]
        interception: Optional[int]
        kneel_down: Optional[int]
        knockdown: Optional[int]
        lost: Optional[int]
        made: Optional[int]
        missed: Optional[int]
        missed_tackles: Optional[int]
        net_yards: Optional[int]
        nullified: Optional[int]
        on_target_throw: Optional[int]
        onside_attempt: Optional[int]
        onside_success: Optional[int]
        opp_rec: Optional[int]
        opp_rec_td: Optional[int]
        opp_rec_yards: Optional[int]
        out_of_bounds: Optional[int]
        own_rec: Optional[int]
        own_rec_yards: Optional[float]
        pass_defended: Optional[int]
        penalty: Optional[int]
        play_category: Optional[str]
        pocket_time: Optional[float]
        primary: Optional[int]
        qb_hit: Optional[int]
        reception: Optional[int]
        return_: Optional[int]
        sack: Optional[int]
        sack_yards: Optional[float]
        scramble: Optional[int]
        squib_kick: Optional[int]
        tackle: Optional[int]
        target: Optional[int]
        tlost: Optional[int]
        tlost_yards: Optional[int]
        touchback: Optional[int]
        touchdown: Optional[int]
        yards: Optional[int]
        yards_after_catch: Optional[int]
        yards_after_contact: Optional[int]


    @dataclass
    class X:
        val1: int
        stats: Sequence[Statistic]

    input = {"val1": 1, "stats": [{"stat_type": "s1"}]}
    from_dict(X, input, Config(strict=True))

    num = 10_000
    t = timeit(lambda: from_dict(X, input, Config(strict=True)), number=num)
    print(t)
    avg = t / num
    print(avg)
    assert avg < 0.00028
    assert avg > 0.00021
    # not copying field reduces time from 40-55ms down to 23-28ms
    # fn optimizations saves a couple ms on the low end
