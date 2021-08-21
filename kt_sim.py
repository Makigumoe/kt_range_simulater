import random
import matplotlib.pyplot as plt
from collections import defaultdict


def damage_cal(hit_norm, hit_crit, save_norm, save_crit, normal, critical, mw, target):
    # 结算摸头
    damage = hit_crit * mw

    # 暴击相互抵消
    if hit_crit > save_crit:
        hit_crit -= save_crit
        save_crit = 0
    else:
        save_crit -= hit_crit
        hit_crit = 0

    # 2普通防御抵消1攻击暴击
    while hit_crit > 0 and save_norm >= 2:
        save_norm -= 2
        hit_crit -= 1

    hit_norm = max(0, hit_norm - save_crit - save_norm)

    damage += hit_norm * normal + hit_crit * critical
    if "fnp" in target:
        temp = 0
        fnp = target["fnp"]
        for _ in range(damage):
            if random.randint(1, 6) < fnp:
                temp += 1
        damage = temp

    return damage


def common_damage(weapon_profile, target, in_cover):
    ap = weapon_profile['ap']
    hits = weapon_profile["hits"]
    bs = weapon_profile["bs"]
    normal, critical = weapon_profile['normal'], weapon_profile["critical"]

    mw = weapon_profile["mw"]

    hit_part = True
    if hit_part:
        hit_norm, hit_crit = 0, 0
        if "auto_1_hit_success" in weapon_profile:
            hits -= 1
            hit_norm += 1

        hit_1_rerolls, hit_any_rerolls = 0, 0
        if "reroll_1_any" in weapon_profile:
            hit_any_rerolls = 1
        if "reroll_any_any" in weapon_profile:
            hit_any_rerolls = hits
        if "reroll_1_1" in weapon_profile:
            hit_1_rerolls = 1
        if "reroll_any_1" in weapon_profile:
            hit_1_rerolls = hits

        hit_roll = [random.randint(1, 6) for _ in range(hits)]

        hit_crit_thershold = 6
        if "grav" in weapon_profile and target["sv"] <= 3:
            hit_crit_thershold = 4

        for h in hit_roll:
            # 重骰:
            if h == 1:
                if hit_1_rerolls > 0:
                    h = random.randint(1, 6)
                    hit_1_rerolls -= 1
                elif hit_any_rerolls > 0:
                    h = random.randint(1, 6)
                    hit_any_rerolls -= 1
            elif h < bs:
                if hit_any_rerolls > 0:
                    h = random.randint(1, 6)
                    hit_any_rerolls -= 1

            if h >= hit_crit_thershold:
                hit_crit += 1
            elif h >= bs:
                hit_norm += 1

        if "P" in weapon_profile and hit_crit > 0:
            ap = weapon_profile["ap"] + weapon_profile["P"]

        if "rending" in weapon_profile and hit_crit > 0:
            if hit_norm > 0:
                hit_norm -= 1
                hit_crit += 1

    save_part = True
    if save_part:
        df, sv = target['df'], target['sv']

        df = max(0, df - ap)

        if in_cover and df > 0:
            df -= 1
            save_norm = 1
        else:
            save_norm = 0

        save_roll = [random.randint(1, 6) for _ in range(df)]
        save_crit = 0

        save_1_rerolls, save_any_rerolls = 0, 0
        if "reroll_1_any" in target:
            save_any_rerolls = 1
        if "reroll_any_any" in target:
            save_any_rerolls = df
        if "reroll_1_1" in target:
            save_1_rerolls = 1
        if "reroll_any_1" in target:
            save_1_rerolls = df

        for s in save_roll:
            # 重骰
            if s == 1:
                if save_1_rerolls > 0:
                    s = random.randint(1, 6)
                    save_1_rerolls -= 1
                elif save_any_rerolls > 0:
                    s = random.randint(1, 6)
                    save_any_rerolls -= 1
            elif s < sv:
                if save_any_rerolls > 0:
                    s = random.randint(1, 6)
                    save_any_rerolls -= 1

            if s == 6:
                save_crit += 1
            elif s >= sv:
                save_norm += 1

        damage_sv = damage_cal(hit_norm, hit_crit, save_norm, save_crit, normal, critical, mw, target)

    sp_save_part = True
    if sp_save_part and "sp_sv" in target:
        df, sv = target['df'], target['sp_sv']

        if in_cover:
            df -= 1

        save_roll = [random.randint(1, 6) for _ in range(df)]
        save_crit = 0
        save_norm = 1 if in_cover else 0

        save_1_rerolls, save_any_rerolls = 0, 0
        if "reroll_1_any" in target:
            save_any_rerolls = 1
        if "reroll_any_any" in target:
            save_any_rerolls = df
        if "reroll_1_1" in target:
            save_1_rerolls = 1
        if "reroll_any_1" in target:
            save_1_rerolls = df

        for s in save_roll:
            # 重骰
            if s == 1:
                if save_1_rerolls > 0:
                    s = random.randint(1, 6)
                    save_1_rerolls -= 1
                elif save_any_rerolls > 0:
                    s = random.randint(1, 6)
                    save_any_rerolls -= 1
            elif s < sv:
                if save_any_rerolls > 0:
                    s = random.randint(1, 6)
                    save_any_rerolls -= 1

            if s == 6:
                save_crit += 1
            elif s >= sv:
                save_norm += 1

        damage_sp_sv = damage_cal(hit_norm, hit_crit, save_norm, save_crit, normal, critical, mw, target)
    else:
        damage_sp_sv = 0

    return damage_sv, damage_sp_sv


weapon_profiles = {
    "boltgun": defaultdict(int, {"hits": 4, "bs": 3, "normal": 3, "critical": 4}),
    "flamer": defaultdict(int, {"hits": 5, "bs": 2, "normal": 2, "critical": 2}),
    "blight_launcher": defaultdict(int, {"hits": 4, "bs": 3, "normal": 4, "critical": 6, "ap": 1}),
    "plague_spewer": defaultdict(int, {"hits": 6, "bs": 2, "normal": 2, "critical": 3}),
    "plasma": defaultdict(int, {"hits": 4, "bs": 3, "normal": 5, "critical": 6, "ap": 1}),
    "plasma_overcharge": defaultdict(int, {"hits": 4, "bs": 3, "normal": 5, "critical": 6, "ap": 2}),
    "guide_missle": defaultdict(int, {"hits": 4, "bs": 3, "normal": 4, "critical": 6, "ap": 1}),
    "ork_snipe": defaultdict(int, {"hits": 6, "bs": 3, "normal": 2, "critical": 2, "mw": 2}),
    "ig_snipe": defaultdict(int, {"hits": 4, "bs": 3, "normal": 3, "critical": 3, "mw": 3}),
    "hotshot_array": defaultdict(int, {"hits": 5, "bs": 3, "normal": 3, "critical": 4, "ap": 1}),
    "ranger_snipe": defaultdict(int, {"hits": 4, "bs": 2, "normal": 3, "critical": 3, "mw": 1}),
    "combi_grav": defaultdict(int, {"hits": 4, "bs": 3, "normal": 4, "critical": 5, "ap": 1, "grav": 1}),
    "combi_melta": defaultdict(int, {"hits": 4, "bs": 3, "normal": 6, "critical": 3, "ap": 2, "mw": 4}),
    "frag_cannon_shell": defaultdict(int, {"hits": 4, "bs": 3, "normal": 5, "critical": 6, "ap": 1, }),
    "heavy_bolter": defaultdict(int, {"hits": 5, "bs": 3, "normal": 4, "critical": 5, "P": 1, }),
    "storm_bolter": defaultdict(int, {"hits": 4, "bs": 3, "normal": 3, "critical": 4, "reroll_any_any": 1}),
    "psy_storm_bolter": defaultdict(int, {"hits": 4, "bs": 3, "normal": 4, "critical": 5, "reroll_any_any": 1}),
    "dw_bolt_hellfire": defaultdict(int, {"hits": 4, "bs": 3, "normal": 3, "critical": 4, "rending": 1}),
    "dw_bolt_kraken": defaultdict(int, {"hits": 4, "bs": 3, "normal": 3, "critical": 4, "P": 1}),
    "dw_bolt_vengeance": defaultdict(int, {"hits": 4, "bs": 3, "normal": 4, "critical": 4, }),
    "psilencer": defaultdict(int, {"hits": 6, "bs": 3, "normal": 3, "critical": 4, }),
    "psycannon": defaultdict(int, {"hits": 5, "bs": 3, "normal": 4, "critical": 6, }),
    "pulse_cannon": defaultdict(int, {"hits": 6, "bs": 4, "normal": 3, "critical": 4, "reroll_any_1": 1,
                                      }),

}

victims = {
    "ig": {'W': 7, "df": 3, "sv": 5, "sp_sv": 5},
    "cornman_shield": {'W': 18, "df": 3, "sv": 2, "sp_sv": 4},
    "nec_warrior": {'W': 9, "df": 3, "sv": 4},
    "plague_marine": {'W': 12, "df": 3, "sv": 3, "fnp": 5},
    "dw_captain": {'W': 12, "df": 3, "sv": 3, "sp_sv": 4},
    "dw_fighter": {'W': 11, "df": 3, "sv": 3, "sp_sv": 4},
}
max_shots = 10
iters = 100000
weapon = "combi_melta"
victim = "cornman_shield"
in_cover = False

kill_count = [0 for _ in range(max_shots)]
kill_count_sp = [0 for _ in range(max_shots)]
for k in range(iters):
    if k % 1000 == 0:
        print(k)
    W1, W2 = victims[victim]['W'], victims[victim]['W']
    fin1, fin2 = False, False
    for i in range(max_shots):
        dam, dam_sp = common_damage(weapon_profiles[weapon], victims[victim], in_cover)
        W1 -= dam
        W2 -= dam_sp
        if W1 <= 0 and not fin1:
            kill_count[i] += 1
            fin1 = True
        if W2 <= 0 and not fin2:
            kill_count_sp[i] += 1
            fin2 = True

        if fin1 and fin2:
            break

average = 0.
prob_max = 0.
for i, n in enumerate(kill_count):
    average += (i + 1) * n
    prob_max = max(prob_max, n)
average /= sum(kill_count)
prob_max = prob_max / iters * 100

kill_count = list(map(lambda x: x / float(iters) * 100, kill_count))

print(kill_count)

x = list(range(1, len(kill_count) + 1))
l1, = plt.plot(x, kill_count, 'b')
# plt.xticks(range(1, 11, 1))
# plt.plot([average], [prob_max + 5], 'r')
plt.annotate('avg num of shoots to kill: {:.2f} using sv'.format(average),
             xy=(average, prob_max + 5),
             xytext=(average, prob_max),
             xycoords='data',
             arrowprops=dict(arrowstyle='->'))  # 添加注释

if sum(kill_count_sp) > 0:
    average_sp = 0.
    prob_max_sp = 0.
    for i, n in enumerate(kill_count_sp):
        average_sp += (i + 1) * n
        prob_max_sp = max(prob_max_sp, n)
    average_sp /= sum(kill_count_sp)
    prob_max_sp = prob_max_sp / iters * 100

    kill_count_sp = list(map(lambda x: x / float(iters) * 100, kill_count_sp))
    print(kill_count_sp)

    l2, = plt.plot(x, kill_count_sp, 'r')
    plt.annotate('avg num of shoots to kill: {:.2f} using isv'.format(average_sp),
                 xy=(average_sp, prob_max_sp + 7 if prob_max_sp > prob_max else prob_max_sp + 3),
                 xytext=(average_sp, prob_max_sp + 2 if prob_max_sp > prob_max else prob_max_sp - 2),
                 xycoords='data',
                 arrowprops=dict(arrowstyle='->'))

    plt.legend(handles=[l1, l2], labels=['using sv', 'using isv'], loc='best')

plt.ylim(0, 80)
plt.title("{} to kill W {} df {} sv {}+ ({})".format(weapon,
                                                     victims[victim]['W'],
                                                     victims[victim]['df'],
                                                     victims[victim]['sv'],
                                                     victim + " in cover" if in_cover else victim))
plt.xlabel("num of shoot actions")
plt.ylabel("prob of kill (%)")
plt.xticks(range(1, 11, 1))
plt.show()
