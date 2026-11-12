---
tags: meta
---
# Native task panel

Native SilverBullet views and actions. Task data stays in existing Markdown;
headless adapter handles offline events and exact WEP approvals.

```space-lua
-- priority: -10
nativeTasks = {}
local api = __NATIVE_CORE__
local core = api.nativeTracker
local function text(value)
  if type(value) ~= "string" then return "" end
  return value:match("^%s*(.-)%s*$")
end

local function values(value)
  if type(value) == "table" then return value end
  local result = {}
  if type(value) == "string" then
    for v in value:gmatch("[^,%s]+") do table.insert(result, v) end
  end
  return result
end

local function day(value)
  local result = text(value):match("^(%d%d%d%d%-%d%d%-%d%d)")
  if not result then return "" end
  local y, m, d = result:match("^(%d%d%d%d)%-(%d%d)%-(%d%d)$")
  y, m, d = tonumber(y), tonumber(m), tonumber(d)
  if y < 1 or m < 1 or m > 12 then return "" end
  local days = {31,28,31,30,31,30,31,31,30,31,30,31}
  if y % 400 == 0 or (y % 4 == 0 and y % 100 ~= 0) then days[2] = 29 end
  if d < 1 or d > days[m] then return "" end
  return result
end

local function bucket(tags, status, category)
  local explicit = text(category):lower()
  if explicit ~= "" then
    local allowed = {daily=true, do_=true, defer=true, delegate=true, delete=true, dump=true, done=true}
    if allowed[explicit == "do" and "do_" or explicit] then return string.upper(explicit) end
    return "Bez kategorii / do sprawdzenia"
  end
  if status == "cancelled" then return "DELETE" end
  local found = nil
  local allowed = {daily=true, do_=true, defer=true, delegate=true, delete=true, dump=true, done=true}
  for _, tag in ipairs(values(tags)) do
    local name = text(tag):gsub("^#", ""):gsub("^6d/", ""):gsub("^5d/", "")
    if allowed[name == "do" and "do_" or name] then
      if found and found ~= name then return "Bez kategorii / do sprawdzenia" end
      found = name
    end
  end
  return found and string.upper(found) or "Bez kategorii"
end

local function project(value)
  local name = text(value)
  return name:match("^%[%[(.-)|.-%]%]$") or name:match("^%[%[(.-)%]%]$") or name
end

function nativeTasks.normalise(pages, today)
  local rows = {}
  for _, p in ipairs(pages) do
    if p.type == "task" and text(p.name) ~= "" then
      local client = text(p.client)
      if client == "" then
        for _, context in ipairs(values(p.contexts)) do
          local candidate = text(context):match("^client/(.+)$")
          if candidate then client = candidate; break end
        end
      end
      local projects = {}
      local primary = project(p.project)
      if primary ~= "" then table.insert(projects, primary)
      else
        for _, name in ipairs(values(p.projects)) do
          local value = project(name)
          if value ~= "" then table.insert(projects, value) end
        end
      end
      if #projects == 0 then table.insert(projects, "Bez projektu") end
      local author = text(p.author):lower() == "ai" and "ai" or "human"
      local status = text(p.status):lower()
      if status == "" then status = "brak statusu" end
      local scheduled = day(p.scheduled)
      local category = bucket(p.tags, status, p.category)
      local completed = status == "done" or (category == "DONE" and status == "brak statusu")
      if category == "DONE" then category = "Bez kategorii / do sprawdzenia" end
      local active = not completed and category ~= "DELETE" and status ~= "cancelled" and status ~= "canceled" and status ~= "archived"
      table.insert(rows, {
        name = p.name, title = text(p.title) ~= "" and text(p.title) or p.name,
        author = author, task_id = text(p.task_id), created_at = text(p.created_at), completed_at = text(p.completed_at), conflicted = p.name:find(".conflicted-", 1, true) ~= nil,
        display_ref = p.name .. "|" .. (completed and "DONE " or "") .. (author == "ai" and "AI " or "") .. (text(p.title) ~= "" and text(p.title) or p.name):gsub("&", "&amp;"):gsub("%[", "&#91;"):gsub("%]", "&#93;"):gsub("|", "&#124;"):gsub("[\r\n]", " "),
        status = status, priority = text(p.priority), client = client ~= "" and client or "Bez klienta",
        project = table.concat(projects, ", "), projects = projects,
        category = category, scheduled = scheduled,
        clientValue = client, projectValue = primary ~= "" and primary or (#projects == 1 and projects[1] == "Bez projektu" and "" or table.concat(projects, ", ")),
        completed = completed, active = active, today = active and scheduled ~= "" and scheduled == today,
      })
    end
  end
  table.sort(rows, function(a,b)
    if a.author ~= b.author then return a.author == "human" end
    if a.completed ~= b.completed then return not a.completed end
    if a.title == b.title then return a.name < b.name end
    return a.title < b.title
  end)
  return rows
end


local SEP = string.char(31)
local categories = {"do", "defer", "delegate", "delete", "dump"}
local routes = {dashboard="index", daily="views/daily", due="views/due", all="views/all", done="views/completed"}
for _, name in ipairs(categories) do routes[name] = "views/" .. name end
local function array(value) return type(value) == "table" and value or {} end
local function state() return js.tolua(core.snapshot()) end
local function prefs() return js.tolua(core.preferences()) end
local function refresh() event.dispatch("nativeTasks:views", {}) end
local function openTask(page) editor.navigate(page) end
local function choose(label, options)
  local selected = editor.filterBox(label, options)
  return selected and selected.value or nil
end
local function prompt(label, value)
  return editor.prompt(label, value or "")
end
local function apply(expectedPage, change)
  if editor.getCurrentPage() ~= expectedPage then error("Otwarta strona zmieniła się.") end
  local before = editor.getText()
  local patch = js.tolua(change(before))
  if patch.unchanged then return before end
  if editor.getCurrentPage() ~= expectedPage or editor.getText() ~= before then error("Treść zadania zmieniła się.") end
  editor.replaceRange(patch.from, patch.to, patch.insert)
  editor.save()
  event.dispatch("nativeTasks:state", {})
  refresh()
  return editor.getText()
end
local function task()
  local page, source = editor.getCurrentPage(), editor.getText()
  if not api.taskPage(source) then error("Otwórz poprawne zadanie type: task.") end
  local meta=js.tolua(core.taskMeta(source))
  if meta.task_id and meta.task_id ~= "" then
    local matches=query[[from p = index.pages() where p.type == "task" and p.task_id == meta.task_id select p]]
    if #matches > 1 then error("Powtórzone ID zadania. Rozstrzygnij konflikt plików przed zmianą statusu lub pomiarem.") end
  end
  return page, source, meta
end
local function bridge()
  return js.tojs(function(operation, serialized)
    local payload = js.tolua(js.window.JSON.parse(serialized))
    if operation == "identity" or operation == "current" then
      if editor.getCurrentPage() ~= payload.page then error("Otwarta strona zmieniła się.") end
      local source = editor.getText()
      if not api.taskPage(source) then error("To nie jest jednoznaczne zadanie.") end
      if operation == "identity" then
        return apply(payload.page, function(before) return core.identityEdit(before) end)
      end
      return source
    end
    if operation == "list" then return js.tojs(space.listPages()) end
    local name = payload.page or ""
    if not (name:match("^tracker%-outbox/") or name:match("^tracker%-acks/") or name:match("^tracker%-cache/") or name:match("^tracker%-drafts/")) or name:find("..",1,true) or name:find("\\",1,true) then error("Nieprawidłowa ścieżka trackera.") end
    if operation == "read" then return space.readPage(name) end
    if operation == "write" then space.writePage(name, payload.text); return true end
    error("Nieznana operacja trackera.")
  end)
end

function nativeTasks.rows(kind, includeDone)
  local today = core.today()
  local result = {}
  local pages = query[[from p = index.pages() where p.type == "task" select p]]
  for _, row in ipairs(nativeTasks.normalise(pages, today)) do
    local actionable = row.category ~= "DELETE" and row.status ~= "cancelled" and row.status ~= "canceled" and row.status ~= "archived" and row.status ~= "deleted"
    local selected = kind == "all" or kind == "dashboard" or (kind == "done" and row.completed and row.category ~= "DELETE") or (kind == "daily" and actionable and row.scheduled == today) or (kind == "due" and actionable and row.scheduled ~= "" and row.scheduled ~= today) or (row.category:lower() == kind and (kind == "delete" or actionable or row.completed))
    if selected and (kind == "delete" or kind == "done" or includeDone or not row.completed) then
      row.sourceName = row.name
      row.displayTitle = (row.completed and "DONE " or "") .. (row.author == "ai" and "AI " or "") .. row.title
      local short = #row.displayTitle > 24 and row.displayTitle:sub(1,24) .. "…" or row.displayTitle
      row.fieldRef = row.sourceName .. "|" .. short:gsub("&","&amp;"):gsub("%[","&#91;"):gsub("%]","&#93;"):gsub("|","&#124;"):gsub("[\r\n]"," ")
      local general = row.clientValue == "" and row.projectValue == ""
      row.groupClient = general and "Ogólne" or row.client
      row.groupProject = general and "" or row.project
      row.groupOrder = general and 0 or (row.clientValue == "" and 1 or 2)
      row.categoryOrder = 9
      for n, name in ipairs(categories) do if row.category:lower() == name then row.categoryOrder = n end end
      local pieces = {}
      if row.scheduled ~= "" then table.insert(pieces, row.scheduled == today and "Dzisiaj" or row.scheduled) end
      if row.priority ~= "" then table.insert(pieces, "Priorytet: " .. row.priority) end
      if kind == "done" then table.insert(pieces, row.completed_at ~= "" and ("Ukończono: " .. row.completed_at) or "Data ukończenia nieznana") end
      row.detail = table.concat(pieces, " · ")
      table.insert(result, row)
    end
  end
  local mode = prefs().sort
  local priorities = {urgent=0, high=1, normal=2, low=3, none=4}
  table.sort(result, function(a,b)
    if kind == "all" and a.categoryOrder ~= b.categoryOrder then return a.categoryOrder < b.categoryOrder end
    if a.groupOrder ~= b.groupOrder then return a.groupOrder < b.groupOrder end
    if a.groupClient ~= b.groupClient then return a.groupClient < b.groupClient end
    if a.groupProject ~= b.groupProject then if a.projectValue == "" or b.projectValue == "" then return a.projectValue == "" end; return a.groupProject < b.groupProject end
    if kind == "done" and a.completed_at ~= b.completed_at then return a.completed_at > b.completed_at end
    if mode == "human" and a.author ~= b.author then return a.author == "human" end
    if a.completed ~= b.completed then return not a.completed end
    local ad,bd = a.scheduled ~= "" and a.scheduled or "9999",b.scheduled ~= "" and b.scheduled or "9999"
    if mode == "date" and ad ~= bd then return ad < bd end
    local ap,bp = priorities[a.priority] or 2,priorities[b.priority] or 2
    if ap ~= bp then return ap < bp end
    if ad ~= bd then return ad < bd end
    if a.author ~= b.author then return a.author == "human" end
    if a.title:lower() ~= b.title:lower() then return a.title:lower() < b.title:lower() end
    return a.sourceName < b.sourceName
  end)
  return result
end

function nativeTasks.add(context)
  context = context or {}
  local title = prompt("Tytuł nowego zadania")
  if not title or title:match("^%s*$") then return end
  local category = context.category
  if category ~= "do" and category ~= "defer" and category ~= "delegate" and category ~= "delete" and category ~= "dump" then
    local options = {}; for _, name in ipairs(categories) do table.insert(options,{name=name:upper(),value=name}) end
    category = choose("Kategoria",options); if not category then return end
  end
  local client = context.client
  if client == nil then client = prompt("Klient (puste = bez klienta)"); if client == nil then return end end
  local project = context.project
  if project == nil then project = prompt("Projekt (puste = bez projektu)"); if project == nil then return end end
  local scheduled = prompt("Termin YYYY-MM-DD (puste = bez terminu)",context.scheduled or "")
  if scheduled == nil then return end
  local created = js.tolua(core.createTask(js.tojs({title=title,category=category,client=client,project=project,scheduled=scheduled})))
  openTask(created.page)
end

function nativeTasks.trash(returnPage)
  local page, source, meta = task()
  if page:find(".conflicted-",1,true) then error("Najpierw rozstrzygnij konflikt plików zadania.") end
  local original = js.tolua(api.metadataValues(source))
  if original.category == "delete" then return end
  for _, run in ipairs(array(state().runs)) do
    if meta.task_id and run.task_id == meta.task_id and (run.state == "active" or run.state == "paused") then
      error("Zakończ pomiar przyciskiem Stop przed przeniesieniem zadania do DELETE.")
    end
  end
  if not editor.confirm("Przenieść zadanie do DELETE?\n\nPlik, treść, ID, autor i historia pozostaną zachowane. Możesz przywrócić zadanie, zmieniając jego kategorię.") then return end
  apply(page,function(before) return api.metadataEdit(before,js.tojs({changes={category="delete"},expected={category=original.category}})) end)
  if returnPage then editor.navigate(returnPage) end
end

function nativeTasks.editMetadata()
  local page, source = task()
  local original = js.tolua(api.metadataValues(source))
  local field = choose("Zmień pole zadania",{{name="Kategoria",value="category"},{name="Termin",value="scheduled"}})
  if not field then return end
  local value
  if field == "category" then
    local options = {};for _, name in ipairs({"do","defer","delegate","delete"}) do table.insert(options,{name=name:upper(),value=name}) end
    value = choose("Nowa kategoria",options)
  else value = prompt("Termin YYYY-MM-DD (puste usuwa termin)",original.scheduled) end
  if value == nil then return end
  local changes,expected = {},{};changes[field]=value;expected[field]=original[field]
  apply(page,function(before) return api.metadataEdit(before,js.tojs({changes=changes,expected=expected})) end)
end

function nativeTasks.complete(action, returnPage)
  local page, source = task()
  local info = js.tolua(api.statusInfo(source))
  local fallback = ""
  if action == "undo" and not info.hasRestore then
    fallback = choose("Poprzedni status starszego zadania",{{name="open — do zrobienia",value="open"},{name="planned — zaplanowane",value="planned"},{name="waiting — oczekujące",value="waiting"},{name="cancelled — odrzucone",value="cancelled"},{name="archived — archiwum",value="archived"}})
    if not fallback then return end
  end
  local checked=js.tolua(api.completionEdit(source,action,fallback));if checked.unchanged then return end
  local receipt = core.beforeCompletion(page,action)
  apply(page,function(before) return core.completionWithLifecycle(before,action,fallback,js.window.JSON.stringify(receipt)) end)
  local value = js.tolua(receipt)
  if action == "complete" and value.run_id then nativeTasks.openDraft(value.run_id)
  elseif returnPage then editor.navigate(returnPage) end
end

function nativeTasks.timer(action)
  local page, source = task()
  if action == "start" and js.tolua(api.metadataValues(source)).category == "delete" then error("Przywróć kategorię zadania z DELETE przed rozpoczęciem pomiaru.") end
  if action == "stop" and not editor.confirm("Czy na pewno zakończyć ten pomiar?\n\nStop zakończy bieżący pomiar i otworzy szkic WEP. Tego pomiaru nie można później wznowić — kolejny Start rozpocznie nowy pomiar.\n\nJeśli chcesz później kontynuować ten sam pomiar, anuluj i wybierz Pauza.\n\nStatus zadania się nie zmieni. Wpis WEP zapisze się dopiero po osobnym zatwierdzeniu.") then return end
  local receipt = js.tolua(core.dispatch(action,page))
  if action == "stop" and receipt.run_id then nativeTasks.openDraft(receipt.run_id) end
end

function nativeTasks.sort()
  local value = choose("Sortowanie w obrębie projektu",{{name="Moje przed AI",value="human"},{name="Ważność najpierw",value="importance"},{name="Termin najpierw",value="date"}})
  if value then core.preference("sort",value);refresh() end
end
function nativeTasks.toggleDone()
  core.preference("showCompleted",not prefs().showCompleted);refresh()
end

function nativeTasks.workspace(kind, mode)
  local contexts = {}
  return widget.new {
    title=kind == "dashboard" and "DAILY" or kind:upper(),stateKey="native-task-" .. kind .. "-" .. (mode or "tree"),
    refreshOn={"index","navigate","nativeTasks:views"},
    source=function()
      contexts = {}
      local selected = kind == "dashboard" and "daily" or kind
      local rows = nativeTasks.rows(selected,prefs().showCompleted)
      if mode ~= "table" then
        for _, row in ipairs(rows) do
          local category = row.category:lower()
          local root = kind == "all" and row.category .. SEP or ""
          if kind == "all" then contexts[row.category] = {category=category} end
          local clientPath = root .. row.groupClient
          contexts[clientPath] = {category=category,client=row.clientValue,project="",scheduled=selected == "daily" and core.today() or ""}
          local prefix = clientPath
          if row.groupProject ~= "" then prefix=prefix .. SEP .. row.groupProject;contexts[prefix]={category=category,client=row.clientValue,project=row.projectValue,scheduled=selected == "daily" and core.today() or ""} end
          row.name = prefix .. SEP .. row.sourceName
        end
      end
      return rows
    end,
    presentation=mode == "table" and {mode="table",limit=10000,columns={
      {attribute="fieldRef",label="Zadanie",type="ref"},{attribute="clientValue",label="Klient",type="text"},{attribute="projectValue",label="Projekt",type="text"},{attribute="author",label="Autor",type="text"},{attribute="priority",label="Priorytet",type="text"},{attribute="scheduled",label="Termin",type="text"},{attribute="completed_at",label="Ukończono",type="text"},
    }} or {mode="tree",limit=10000,hierarchy={field="name",separator=SEP},expandAll=true,row={primary="displayTitle",label="displayTitle",description="detail",cssClass=function(row) return row.isFolder and "" or "native-task-row" end,icon=function(row) return row.isFolder and "folder" or (row.completed and "check-circle" or "circle") end,decorations=function(row) return row.conflicted and {{text="Konflikt plików",icon="alert-triangle",position="right"}} or {} end}},
    filter={inline=true,fields={title=4,client=2,project=2,author=1,scheduled=1}},
    onSelect=function(row) if not row.isFolder then openTask(row.sourceName) end end,
    actions={
      {icon="plus",label="Dodaj zadanie tutaj",when=function(row) return row.isFolder and contexts[row.name] ~= nil end,run=function(row) nativeTasks.add(contexts[row.name]) end},
      {icon="file-text",label="Otwórz zadanie",when=function(row) return not row.isFolder end,run=function(row) openTask(row.sourceName) end},
      {icon="check",label="Oznacz jako DONE",when=function(row) return not row.isFolder and not row.completed and not row.conflicted end,run=function(row) openTask(row.sourceName);nativeTasks.complete("complete",routes[kind]) end},
      {icon="rotate-ccw",label="Cofnij DONE",when=function(row) return not row.isFolder and row.completed and not row.conflicted end,run=function(row) openTask(row.sourceName);nativeTasks.complete("undo",routes[kind]) end},
      {icon="trash-2",label="Przenieś do DELETE",when=function(row) return not row.isFolder and not row.conflicted and row.category ~= "DELETE" end,run=function(row) openTask(row.sourceName);nativeTasks.trash(routes[kind]) end},
    },
  }
end
function nativeTasks.sidebar()
  local result = {
    {name="add",title="ADD",icon="plus",action="add"},
    {name="index",title="DASHBOARD",icon="home",page="index"},
  }
  for _, item in ipairs({{"daily","DAILY","calendar"},{"due","DUE","calendar"},{"done","DONE","check-circle"}}) do
    table.insert(result,{name=item[1],title=item[2],icon=item[3],page=routes[item[1]],count=#nativeTasks.rows(item[1],false)})
  end
  local pending = 0;for _, run in ipairs(array(state().runs)) do if (run.state == "stopped" or run.state == "conflict") and not run.receipt then pending=pending+1 end end
  table.insert(result,{name="wep",title="WEP",icon="clock",page="views/tracker",count=pending})
  table.insert(result,{name="all",title="ALL",icon="list",page=routes.all,count=#nativeTasks.rows("all",false)})
  for _, category in ipairs(categories) do table.insert(result,{name=category,title=category:upper(),icon="list",page=routes[category],count=#nativeTasks.rows(category,false)}) end
  for _, run in ipairs(array(state().runs)) do
    if run.state == "active" or run.state == "paused" then
      local page=not run.context_error and run.path and run.path:gsub("%.md$", "") or "views/tracker"
      local title=run.path and run.path:match("([^/]+)%.md$") or run.task_id
      table.insert(result,{name="timer-" .. run.id,title=(run.state == "active" and "Trwa pomiar: " or "Pauza: ") .. title,description=core.duration(core.elapsed(js.tojs(run))),icon="clock",page=page})
    end
  end
  return result
end
function nativeTasks.dashboard()
  return widget.new {
    title="Podsumowanie",refreshOn={"index","navigate","nativeTasks:state"},
    source=function()
      local result = {}
      for _, item in ipairs({{"daily","DAILY — dzisiaj"},{"due","DUE — pozostałe terminy"},{"done","DONE — ukończone"}}) do table.insert(result,{name=item[1],title=item[2],count=#nativeTasks.rows(item[1],false),page=routes[item[1]]}) end
      local pending=0;for _, run in ipairs(array(state().runs)) do if (run.state == "stopped" or run.state == "conflict") and not run.receipt then pending=pending+1 end end
      table.insert(result,{name="wep",title="Szkice WEP do sprawdzenia",count=pending,page="views/tracker"})
      return result
    end,
    presentation={mode="table",columns={{attribute="title",label="Widok",type="text"},{attribute="count",label="Liczba",type="number"}}},
    onSelect=function(row) editor.navigate(row.page) end,
  }
end

local function runPath(run)
  if run.context_error or not run.path or run.path == "" then error("Nie można bezpiecznie powiązać sesji z zadaniem: " .. (run.context_error or "brak ścieżki")) end
  return run.path:gsub("%.md$", "")
end
function nativeTasks.openDraft(id)
  core.selectRun(id)
  editor.navigate("views/wep")
end
function nativeTasks.trackerQueue()
  return widget.new {
    title="Timer i WEP",refreshOn={"index","navigate","nativeTasks:state"},
    source=function()
      local result={}
      for _, run in ipairs(array(state().runs)) do
        if run.state ~= "discarded" then
          local row = {name=run.id,id=run.id,title=run.path and run.path:gsub("%.md$",""):match("[^/]+$") or run.task_id,status=run.state,elapsed=core.duration(core.elapsed(js.tojs(run))),review=run.review == 1 or run.state == "conflict",approved=run.receipt ~= nil and run.receipt ~= false,path=run.path,context_error=run.context_error}
          if run.receipt then row.status="WEP zatwierdzony" end
          table.insert(result,row)
        end
      end
      return result
    end,
    presentation={mode="table",columns={{attribute="title",label="Zadanie",type="text"},{attribute="status",label="Stan",type="text"},{attribute="elapsed",label="Czas",type="text"},{attribute="review",label="Przegląd czasu",type="boolean"},{attribute="approved",label="WEP",type="boolean"}}},
    filter={inline=true,fields={title=3,status=1}},
    onSelect=function(row) nativeTasks.openDraft(row.id) end,
    actions={{icon="file-text",label="Otwórz zadanie",when=function(row) return not row.context_error and row.path and row.path ~= "" end,run=function(row) editor.navigate(row.path:gsub("%.md$","")) end}},
  }
end
local function selectedRun()
  return js.tolua(core.selectedRun())
end
local function loadedDraft(run)
  return js.tolua(core.getDraft(run.id))
end
local function saveDraft(run,draft)
  core.saveDraft(run.id,js.tojs(draft))
end

function nativeTasks.editDraft(field)
  local run=selectedRun();if not run or run.receipt then return end
  local draft=loadedDraft(run)
  if field == "outcome" then
    local value=prompt("Wynik wykonanej pracy",draft.outcome or "");if value == nil then return end;draft.outcome=value
  elseif field == "client" or field == "project" then
    local choices={{name="Bez przypisania",value=""}}
    for _, entity in ipairs(array(state().entities)) do
      if entity.kind == field and (field ~= "project" or not entity.parent_id or entity.parent_id == draft.client_id) then table.insert(choices,{name=(entity.aliases and entity.aliases[1]) or entity.id,value=entity.id}) end
    end
    local value=choose(field == "client" and "Klient WEP" or "Projekt WEP",choices);if value == nil then return end
    if field == "client" then draft.client_id=value;draft.project_id="" else draft.project_id=value end
    draft.unassigned_confirmed=false
  elseif field == "unassigned" then
    draft.unassigned_confirmed=editor.confirm("Potwierdzasz zapis WEP bez brakującego przypisania klienta lub projektu?")
  elseif field == "time-confirmed" then
    draft.time_confirmed=editor.confirm("Potwierdzasz, że wskazany czas jest rzeczywistym czasem Twojej pracy? Oryginalny pomiar pozostanie w historii.")
  elseif field == "time" then
    draft.days=draft.days or {}
    if next(draft.days) == nil then
      local days=js.tolua(core.daysFor(run.id));for day,seconds in pairs(days) do draft.days[day]=seconds ~= nil and tostring(seconds/60) or "" end
    end
    local options={};for day,minutes in pairs(draft.days) do table.insert(options,{name=day .. " — " .. tostring(minutes) .. " min",value=day}) end
    table.insert(options,{name="Dodaj dzień korekty",value="add"})
    local day=choose("Dzień korekty czasu",options);if not day then return end
    if day == "add" then day=prompt("Dzień korekty YYYY-MM-DD");if not day then return end;if not api.validDay(day) then error("Niepoprawna data korekty.") end end
    local minutes=prompt("Rzeczywiste minuty pracy " .. day,draft.days[day] or "");if minutes == nil then return end
    local number=tonumber(minutes:gsub(",","."));if not number or number < 0 then error("Podaj liczbę minut; zero wpisz jawnie.") end
    local reason=prompt("Powód korekty czasu (wymagany)",draft.reason or "");if not reason then return end;if reason:match("^%s*$") then error("Podaj powód korekty.") end
    draft.days[day]=tostring(number);draft.reason=reason;draft.correct=true;draft.time_confirmed=false
  elseif field == "original-time" then
    draft.correct=false;draft.reason="";draft.time_confirmed=false
  else error("Nieznane pole szkicu.") end
  saveDraft(run,draft)
end

function nativeTasks.wepAction(action)
  local run=selectedRun();if not run then return end
  if action == "task" then editor.navigate(runPath(run));return end
  if action == "preview" then core.preparePreview(run.id);return end
  if action == "approve" then
    local preview=js.tolua(core.previewFor(run.id));if not preview then error("Przygotuj aktualny podgląd WEP.") end
    if not editor.confirm("Zatwierdzić ten wpis WEP?\n\nWynik: " .. (preview.outcome or "") .. "\nCzas: " .. core.duration(preview.total_seconds) .. "\nKlient: " .. (preview.client_id or "bez przypisania") .. "\nProjekt: " .. (preview.project_id or "bez przypisania") .. "\nPodgląd: " .. preview.preview_hash:sub(1,16)) then return end
    local saved=js.tolua(core.approvePreview(run.id,preview.preview_hash))
    editor.flashNotification(saved.xlsx_status == "current" and "WEP zatwierdzony. Arkusz odświeżony." or "WEP zatwierdzony. Arkusz czeka na odświeżenie.")
    return
  end
  if action == "xlsx" then core.refreshWorkbook(run.id);return end
  if action == "resolve" or action == "discard" then
    local draft=loadedDraft(run)
    local reason=draft.reason
    if not reason or reason:match("^%s*$") then reason=prompt(action == "discard" and "Powód wyłączenia sesji z WEP" or "Powód rozstrzygnięcia czasu");if not reason then return end end
    if reason:match("^%s*$") then error("Podaj powód.") end
    if action == "discard" and not editor.confirm("Wyłączyć tę sesję z WEP? Zdarzenia i powód pozostaną w historii.") then return end
    local correction=action == "resolve" and core.timeCorrection(js.tojs(draft)) or nil
    editor.navigate(runPath(run))
    core.dispatch(action,editor.getCurrentPage(),js.tojs({run_id=run.id,correction=correction,reason=reason}))
    editor.navigate("views/wep")
    return
  end
  error("Nieznana akcja WEP.")
end

function nativeTasks.wepFields()
  return widget.new {
    title="Szkic WEP",refreshOn={"index","navigate","nativeTasks:state"},
    source=function()
      local run=selectedRun();if not run then return {{name="empty",title="Wybierz sesję w widoku Timer i WEP"}} end
      local context=state();local draft=loadedDraft(run);local preview=js.tolua(core.previewFor(run.id))
      local result={{name="task",title="Zadanie",value=run.path or run.task_id,action="task"},{name="status",title="Stan",value=run.state .. (run.receipt and " · WEP zatwierdzony" or "")},{name="measured",title="Oryginalny pomiar",value=core.duration(core.elapsed(js.tojs(run)))},{name="sync",title="Synchronizacja",value=context.online and (context.pending > 0 and "Oczekuje na synchronizację" or "Stan potwierdzony przez serwer") or "Offline — zdarzenia zachowane lokalnie"}}
      if run.receipt then
        table.insert(result,{name="receipt",title="Transakcja WEP",value=run.receipt.transaction_id or "zatwierdzono"})
        if run.receipt.xlsx_status == "pending" then table.insert(result,{name="xlsx",title="Odśwież arkusz",action="xlsx"}) end
        return result
      end
      for _, row in ipairs({
        {name="outcome",title="Wynik pracy",value=draft.outcome or "Uzupełnij wynik",field="outcome"},
        {name="client",title="Klient WEP",value=draft.client_id and draft.client_id ~= "" and draft.client_id or "Bez przypisania",field="client"},
        {name="project",title="Projekt WEP",value=draft.project_id and draft.project_id ~= "" and draft.project_id or "Bez przypisania",field="project"},
        {name="unassigned",title="Brak przypisania potwierdzony",value=draft.unassigned_confirmed and "Tak" or "Nie",field="unassigned"},
        {name="time",title="Korekta czasu z powodem",value=draft.correct and (draft.reason or "Korekta") or "Oryginalny pomiar",field="time"},
        {name="time-confirmed",title="Rzeczywisty czas potwierdzony",value=draft.time_confirmed and "Tak" or "Nie",field="time-confirmed"},
      }) do table.insert(result,row) end
      if draft.correct then
        for day,minutes in pairs(draft.days or {}) do table.insert(result,{name="day-" .. day,title=day,value=tostring(minutes) .. " min",field="time"}) end
        table.insert(result,{name="original-time",title="Przywróć oryginalny pomiar",field="original-time"})
      end
      if run.review == 1 or run.state == "conflict" then
        table.insert(result,{name="resolve",title="Potwierdź rozstrzygnięcie czasu",action="resolve"})
        table.insert(result,{name="discard",title="Wyłącz tę sesję z WEP",action="discard"})
      elseif context.online and context.pending == 0 and not context.busy and run.state == "stopped" then
        table.insert(result,{name="preview",title="Przygotuj podgląd WEP",action="preview"})
        if preview then table.insert(result,{name="approve",title="Zatwierdź wpis WEP",value="Wersja " .. preview.preview_hash:sub(1,16),action="approve"}) end
      else table.insert(result,{name="wait",title="Zatwierdzanie wymaga zakończonej i zsynchronizowanej sesji"}) end
      if context.message and context.message ~= "" then table.insert(result,{name="notice",title="Komunikat",value=context.message}) end
      return result
    end,
    presentation={mode="table",columns={{attribute="title",label="Pole / akcja",type="text"},{attribute="value",label="Wartość",type="text"}}},
    onSelect=function(row) if row.field then nativeTasks.editDraft(row.field) elseif row.action then nativeTasks.wepAction(row.action) end end,
    actions={{icon="edit",label="Edytuj pole",when=function(row) return row.field ~= nil end,run=function(row) nativeTasks.editDraft(row.field) end},{icon="play",label="Wykonaj akcję",when=function(row) return row.action ~= nil end,run=function(row) nativeTasks.wepAction(row.action) end}},
  }
end

function nativeTasks.wepPreview()
  return widget.new {
    title="Podgląd i oryginalne odcinki",refreshOn={"index","navigate","nativeTasks:state"},
    source=function()
      local run=selectedRun();if not run then return {} end
      local preview=js.tolua(core.previewFor(run.id));local result={}
      if preview then
        table.insert(result,{name="outcome",day="Wynik",detail=preview.outcome})
        table.insert(result,{name="allocation",day="Przypisanie",detail=(preview.client_id or "bez klienta") .. " / " .. (preview.project_id or "bez projektu")})
        table.insert(result,{name="result-status",day="Wynik sesji",detail=preview.status})
        table.insert(result,{name="task-ref",day="Powiązanie zadania",detail=preview.task_ref})
        table.insert(result,{name="work-id",day="Identyfikator pracy WEP",detail=preview.task_work_id})
        if preview.evidence then
          table.insert(result,{name="evidence-source",day="Dowód źródłowy",detail=preview.evidence.source})
          table.insert(result,{name="evidence-hash",day="SHA-256 dowodu",detail=preview.evidence.sha256})
        end
        for n,piece in ipairs(array(preview.pieces)) do table.insert(result,{name="piece-" .. n,day=piece.day,start=piece.start or "",finish=piece["end"] or "",duration=core.duration(piece.seconds),basis=piece.basis}) end
        table.insert(result,{name="total",day="SUMA",duration=core.duration(preview.total_seconds),detail="Podgląd " .. preview.preview_hash:sub(1,16)})
      else table.insert(result,{name="no-preview",day="Brak aktualnego podglądu",detail="Po zmianie pól przygotuj nowy podgląd przed zatwierdzeniem."}) end
      for n,segment in ipairs(array(run.segments)) do table.insert(result,{name="original-" .. n,day="Oryginalny odcinek",start=segment.start,finish=segment["end"] or "trwa",basis=segment.basis}) end
      return result
    end,
    presentation={mode="table",columns={{attribute="day",label="Data / opis",type="text"},{attribute="start",label="Początek UTC",type="text"},{attribute="finish",label="Koniec UTC",type="text"},{attribute="duration",label="Czas",type="text"},{attribute="basis",label="Podstawa",type="text"},{attribute="detail",label="Szczegóły",type="text"}}},
  }
end
function nativeTasks.wepHistory()
  return widget.new {
    title="Historia pomiaru",refreshOn={"index","navigate","nativeTasks:state"},
    source=function()
      local run=selectedRun();local result={};if not run then return result end
      for n,entry in ipairs(array(run.events)) do table.insert(result,{name=tostring(n),action=entry.action,time=entry.occurred_at,device=entry.device_id,operation=entry.operation_id}) end
      return result
    end,
    presentation={mode="table",columns={{attribute="action",label="Zdarzenie",type="text"},{attribute="time",label="Chwila UTC",type="text"},{attribute="device",label="Urządzenie",type="text"},{attribute="operation",label="ID operacji",type="text"}}},
  }
end
function nativeTasks.creation()
  return widget.new {source=function() return {{name="add",title="Dodaj zadanie",description="Tytuł, kategoria, klient, projekt i termin",icon="plus"}} end,presentation={mode="list",row={primary="title",description="description",icon=function(row) return row.icon end}},onSelect=function() nativeTasks.add() end}
end
local function mainKind()
  local current=editor.getCurrentPage()
  for kind,page in pairs(routes) do if current == page or current == page .. "-table" then return kind,current:match("%-table$") ~= nil end end
  if current == "views/today" then return "daily",false end
  if current == "views/clients" or current == "views/projects" or current == "views/categories" then return "all",false end
  if current == "views/waiting" then return "delegate",false end
  return nil,false
end
view.define {
  name="kuba.tasks.navigation",title="Zadania",command="Zadania: Pokaż panel",dock="lhs",supportedDocks={"lhs","rhs"},openOnStart=true,
  refreshOn={"index","navigate","nativeTasks:state","nativeTasks:views"},
  source=function() return nativeTasks.sidebar() end,
  presentation={mode="list",row={primary="title",description="description",icon=function(row) return row.icon end,decorations=function(row) return row.count ~= nil and {{text=tostring(row.count),position="right"}} or {} end}},
  onSelect=function(row) if row.action == "add" then nativeTasks.add() elseif row.page then editor.navigate(row.page) end end,
}
view.define {
  name="native.tasks.view-actions",title="Widok",dock="page-top",frame="minimal",defaultOpen=true,
  onSelect=function() end,
  refreshOn={"index","navigate","nativeTasks:views"},
  source=function()
    local kind,tableMode=mainKind();if not kind then return {} end
    return {{name="view",kind=kind,tableMode=tableMode,title=(kind == "dashboard" and "DASHBOARD" or kind:upper()),description=(kind == "done" and "Tylko ukończone" or (prefs().showCompleted and "Z ukończonymi" or "Otwarte")) .. " · " .. (prefs().sort == "human" and "Moje przed AI" or (prefs().sort == "date" and "Termin najpierw" or "Ważność najpierw"))}}
  end,
  presentation={mode="list",row={primary="title",description="description"}},
  actions={
    {icon="plus",label="Dodaj zadanie",run=function(row)
      local context={};for _,name in ipairs(categories) do if row.kind == name then context.category=name end end
      if row.kind == "daily" then context.scheduled=core.today() end
      nativeTasks.add(context)
    end},
    {icon="check-square",label="Pokaż / ukryj ukończone",when=function(row) return row.kind ~= "done" end,run=function() nativeTasks.toggleDone() end},
    {icon="sliders",label="Sortowanie",run=function() nativeTasks.sort() end},
    {icon="columns",label="Przełącz drzewo / tabelę pól",run=function(row) editor.navigate(routes[row.kind] .. (row.tableMode and "" or "-table")) end},
  },
}
view.define {
  name="kuba.tasks.completion",title="Zadanie i timer",dock="page-top",frame="minimal",defaultOpen=true,
  refreshOn={"navigate","nativeTasks:state","nativeTasks:clock"},
  source=function()
    local source=editor.getText();if not api.taskPage(source) then return {} end
    local meta=js.tolua(core.taskMeta(source));local info=js.tolua(api.statusInfo(source));local context=state();local own
    for _,run in ipairs(array(context.runs)) do if run.task_id == meta.task_id and (run.state == "active" or run.state == "paused") then own=run;break end end
    local result={{name="state",title=own and (own.state == "active" and "Trwa pomiar" or "Pauza") or "Timer",description=own and core.duration(core.elapsed(js.tojs(own))) or "Brak otwartego pomiaru",icon="clock"}}
    if not context.busy then
      local deleted=js.tolua(api.metadataValues(source)).category == "delete"
      if not own and not deleted then table.insert(result,{name="start",title="Start",timer="start",icon="play"})
      elseif own then
        table.insert(result,{name="pause-resume",title=own.state == "active" and "Pauza" or "Wznów",timer=own.state == "active" and "pause" or "resume",icon=own.state == "active" and "pause" or "play"})
        table.insert(result,{name="stop",title="Stop",timer="stop",icon="square"})
      end
      if not deleted then table.insert(result,{name="complete",title=info.done and "Cofnij DONE" or "Oznacz jako DONE",status=info.done and "undo" or "complete",icon=info.done and "rotate-ccw" or "check"}) end
      table.insert(result,{name="metadata",title="Kategoria i termin",edit=true,icon="edit"})
      local values=js.tolua(api.metadataValues(source))
      if values.category ~= "delete" then table.insert(result,{name="trash",title="Przenieś do DELETE",trash=true,icon="trash-2"}) end
    end
    for _,run in ipairs(array(context.runs)) do
      if run.task_id == meta.task_id and (run.state == "stopped" or run.state == "conflict") and not run.receipt then table.insert(result,{name=run.id,title=run.review == 1 and "Rozstrzygnij czas" or "Otwórz szkic WEP",description=core.duration(core.elapsed(js.tojs(run))),run=run.id,icon="file-text"}) end
    end
    table.insert(result,{name="sync",title=context.online and (context.pending > 0 and "Oczekuje na synchronizację" or "Stan potwierdzony przez serwer") or "Offline — zdarzenia zapisują się lokalnie",description=context.message or "",icon=context.online and "check" or "cloud-off"})
    return result
  end,
  presentation={mode="list",row={primary="title",description="description",icon=function(row) return row.icon end}},
  onSelect=function(row)
    if row.timer then nativeTasks.timer(row.timer) elseif row.status then nativeTasks.complete(row.status) elseif row.edit then nativeTasks.editMetadata() elseif row.trash then nativeTasks.trash() elseif row.run then nativeTasks.openDraft(row.run) end
  end,
}

command.define {name="Zadania: Dodaj zadanie",run=function() nativeTasks.add() end}
command.define {name="Zadania: Sortowanie",run=function() nativeTasks.sort() end}
command.define {name="Zadania: Pokaż ukończone",run=function() nativeTasks.toggleDone() end}
command.define {name="Zadania: Start",run=function() nativeTasks.timer("start") end}
command.define {name="Zadania: Pauza",run=function() nativeTasks.timer("pause") end}
command.define {name="Zadania: Wznów",run=function() nativeTasks.timer("resume") end}
command.define {name="Zadania: Stop",run=function() nativeTasks.timer("stop") end}
command.define {name="Zadania: DONE",run=function() nativeTasks.complete("complete") end}
command.define {name="Zadania: Cofnij DONE",run=function() nativeTasks.complete("undo") end}
command.define {name="Zadania: Kategoria i termin",run=function() nativeTasks.editMetadata() end}
command.define {name="Zadania: Przenieś do DELETE",run=function() nativeTasks.trash() end}
command.define {name="Zadania: Szkice WEP",run=function() editor.navigate("views/tracker") end}
core.connect(bridge(),js.tojs(function(reason) event.dispatch(reason == "clock" and "nativeTasks:clock" or "nativeTasks:state",{}) end))
```

```space-style
html { --editor-width: 1200px; }
/* Native task leaves only; retain full labels in the data and accessible text. */
#sb-main .sb-inline-view .sb-nav-row.native-task-row {
  flex-wrap: nowrap;
}
#sb-main .sb-inline-view .sb-nav-row.native-task-row .sb-nav-primary {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
#sb-main .sb-inline-view .sb-nav-row.native-task-row .sb-nav-description {
  flex-shrink: 0;
  white-space: nowrap;
}
#sb-main .sb-inline-view .sb-nav-row.native-task-row .sb-nav-chip {
  flex-shrink: 0;
  white-space: nowrap;
  overflow-wrap: normal;
}
#sb-main .sb-inline-view:has(.native-task-row) {
  container-type: inline-size;
}
@container (max-width: 38rem) {
  #sb-main .sb-inline-view .sb-nav-row.native-task-row {
    display: grid;
    grid-template-columns: 1.2rem 1.2rem minmax(0, 1fr) auto;
  }
  #sb-main .sb-inline-view .sb-nav-row.native-task-row .sb-nav-description {
    grid-column: 3 / -1;
    grid-row: 2;
    white-space: normal;
  }
  #sb-main .sb-inline-view .sb-nav-row.native-task-row .sb-nav-chip {
    grid-column: 3 / -1;
    grid-row: 3;
    justify-self: start;
  }
  #sb-main .sb-inline-view .native-task-row .sb-row-actions {
    grid-column: 4;
    grid-row: 1;
  }
}
```
