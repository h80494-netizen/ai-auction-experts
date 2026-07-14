with open("c:/Users/llll/Documents/두인경매/바이브코딩/public/map.html", "r", encoding="utf-8") as f:
    content = f.read()

print("fetchPlanningRoads in map.html:", "fetchPlanningRoads" in content)
print("planning_roads in map.html:", "planning_roads" in content)
print("planningRoads in map.html:", "planningRoads" in content)
print("zoning in map.html:", "zoning" in content)
print("dev3 in map.html:", "dev3" in content)
