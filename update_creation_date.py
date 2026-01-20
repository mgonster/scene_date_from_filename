# Author: Mgonster

from PythonDepManager import ensure_import
ensure_import("stashapi:stashapp-tools>=0.2.58")
import stashapi.log as log
from stashapi.stashapp import StashInterface
import re
from datetime import datetime
from zoneinfo import ZoneInfo
import sys, json

def main():
  global stash
  global pattern
  # I know this is bad, but I can't be bothered to pass it down, and I'm not 
  # the one who started using globals! The other globals are from the template!
  global re_timestamp_ns
  re_timestamp_ns = re.compile(r'\[\[t-(\d+)\]\]')
  

  json_input = json.loads(sys.stdin.read())
  hookContext = json_input['args'].get("hookContext")
  stash = StashInterface(json_input["server_connection"])
  mode_arg = json_input["args"]["mode"]
  if hookContext and (hookContext.get("type") == "Scene.Create.Post"):
    updateSceneByID(hookContext.get('id'))
  elif mode_arg == "undated":
    updateUndatedScenes()
  elif mode_arg == "all":
    updateAllScenes()
  

def updateScene(scene):
  update_scene_graphql = """
  mutation UpdateDate($id: ID!, $date: String!) {
    sceneUpdate(input: { id: $id, date: $date }) {
      id
    }
  }
  """
  id = scene['id']
  for file in scene["files"]:
    file_name = file["basename"]
    re_match = re_timestamp_ns.search(file_name)
    if re_match:
      time_ns = re_match.group(1)
      time_ms = int(time_ns) // 1000000 / 1000
      # birth_timestamp = datetime.fromtimestamp(time_ms, tz=ZoneInfo(""))
      birth_timestamp = datetime.fromtimestamp(time_ms)
      birth_timestring = birth_timestamp.strftime("%Y-%m-%d")
      key_vars = {"id":id, "date":birth_timestring}
      stash.call_GQL(update_scene_graphql, variables=key_vars)

def updateScenes(scenes, total_scenes, current_scene_count):
  for i, scene in enumerate(scenes):
    log.progress((current_scene_count + i) / total_scenes)
    updateScene(scene)

def updateUndatedScenes():
  get_undated_scenes_graphql = """
  query GetUndatedScenes {
    findScenes(scene_filter: { date: { value: "", modifier: IS_NULL } }) {
      count
      scenes {
        id
        files {
          basename
        }
      }
    }
  }
  """
  log.info("Adding dates to undated scenes")
  # it can do 25 an iteration, so it will only do 2500
  iteration_limit = 100
  data = stash.call_GQL(get_undated_scenes_graphql)["findScenes"]
  total_scenes = data['count'] if data['count'] <= 2500 else 2500
  scenes = data['scenes']
  current_scene_count = 0
  while scenes and iteration_limit > 0:
    updateScenes(scenes, total_scenes, current_scene_count)
    scene_count += len(scenes)
    # get new undated scenes
    scenes = stash.call_GQL(get_undated_scenes_graphql)["findScenes"]["scenes"]
    total_iterations -= 1
  log.info(f"Finished updating {scene_count} scenes")
      
def updateAllScenes():
  get_all_scenes_graphql = """
  query GetAllScenes {
    allScenes {
      id
      files {
        basename
      }
    }
  }
  """
  log.info("Updating dates on all scenes")
  scenes = stash.call_GQL(get_all_scenes_graphql)["allScenes"]
  updateScenes(scenes, len(scenes), 0)
  log.info(f"Finished updating {len(scenes)} scenes")

def updateSceneByID(sceneID):
  get_scene_by_id_graphql = """
  query GetSceneByID($id: ID!) {
    findScene(id: $id) {
      id
      files {
        basename
      }
    }
  }
  """
  scene = stash.call_GQL(get_scene_by_id_graphql, variables={"id": sceneID})['findScene']
  updateScene(scene)
  
if __name__ == "__main__":
    main()