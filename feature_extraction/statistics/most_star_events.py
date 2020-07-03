from obj.star_event import get_star_events


star_events = get_star_events()

user_repo_map = dict()
repo_owner = set()

for se in star_events:
    try:
        user_repo_map[se.star_user]
    except KeyError:
        user_repo_map[se.star_user] = set()
    user_repo_map[se.star_user].add((se.repo_owner, se.repo_name))
    repo_owner.add(se.repo_owner)

temp = sorted(user_repo_map, key=lambda x: len(user_repo_map[x]), reverse=True)

# print(len(temp))
#
# for k in range(0,100):
#     print(temp[k])
#     print(len(user_repo_map[temp[k]]))
#
# summary = 0
#
# for k in range(100, len(temp)):
#     summary += len(user_repo_map[temp[k]])
#
#
# print(summary)

for k in temp:
    if k in repo_owner:
        print(k)
        print(user_repo_map[k])
