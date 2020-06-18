-- DEBUGGING
--
-- Debug messages will be printed to stdout with mpv command line option
-- `--msg-level='bookmarker=debug'`

local utils = require('mp.utils')
local msg = require('mp.msg')

--// check whether a file exists or not
function file_exists(path)
  local f = io.open(path, "r")
  if f ~= nil then
    io.close(f)
    return true
  else
    msg.debug("[path/url]", "'" .. path .. "' did not exist.")
    return false
  end
end

--// check if macos
function is_macos()
  local homedir = os.getenv("HOME")
  if homedir ~= nil and string.sub(homedir, 1, 6) == "/Users" then
    msg.debug("[os/detector]", "macOS detected.")
    return true
  else
    return false
  end
end

--// check if windows
function is_windows()
  local windir = os.getenv("windir")
  if windir ~= nil then
    msg.debug("[os/detector]", "windows detected.")
    return true
  else
    return false
  end
end

function platform_independent(filepath)
  return filepath -- // see "shared-bookmarks-different-os.md" to see utility of this function
end

function saveKyykka(time_sec, path, char)
  msg.info(path)
  
  -- Open the file in r mode (don't modify file, just read)
  local f = io.open(path, 'r')
  
  if f == nil then
    f = io.open(path, "w+")
  end

  -- Fetch all lines and add them to a table
  local lines = {}
  local titles = 0
  for line in f:lines() do
      if string.find(line, "*") == 1 then
        titles = titles + 1
      end
      table.insert(lines, line)
  end

  -- Close the file so that we can open it in a different mode
  f:close()

  if char ~= nil then
    table.insert(lines, string.format("%s %.10f", char, time_sec))
    mp.osd_message(string.format("Saved char: %s", char))
  elseif (#lines - titles) % 2 == 0 then
    table.insert(lines, string.format("> %.10f", time_sec))
    mp.osd_message("Cut number 1")

  else
    table.insert(lines, string.format("< %.10f", time_sec))
    mp.osd_message("Cut number 2")
  end

  -- Make the file operational transactional
  local file = io.open(path .. ".tmp", "wb")
  for _, line in ipairs(lines) do
    file:write(line, "\n")
  end

  io.close(file)
  os.remove(path)
  os.rename(path .. ".tmp", path)

  msg.info("kyykka cut file successfully saved.")
  return true
end


function get_cutfile_path()
  dir = mp.get_property("working-directory")
  filename = mp.get_property("filename/no-ext")
  
  msg.info(dir, filename)

  return string.format("%s/%s.txt", dir, filename)
end

function cut_save()
  msg.info("[interface]", "received cut script message.")
  saveKyykka(mp.get_property("time-pos"), get_cutfile_path(), nil)
end
mp.register_script_message("cut", cut_save)

function title_save()
  msg.info("received title script message.")
  saveKyykka(mp.get_property("time-pos"), get_cutfile_path(), "*")
end
mp.register_script_message("title", title_save)

function extra_save()
  msg.info("received extra script message.")
  saveKyykka(mp.get_property("time-pos"), get_cutfile_path(), "|")
end
mp.register_script_message("extra", extra_save)

