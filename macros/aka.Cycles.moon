-- aka.Cycles
-- Copyright (c) Akatsumekusa and contributors

------------------------------------------------------------------------------
-- Permission is hereby granted, free of charge, to any person obtaining a
-- copy of this software and associated documentation files (the "Software"),
-- to deal in the Software without restriction, including without limitation
-- the rights to use, copy, modify, merge, publish, distribute, sublicense,
-- and/or sell copies of the Software, and to permit persons to whom the
-- Software is furnished to do so, subject to the following conditions:

-- The above copyright notice and this permission notice shall be included in
-- all copies or substantial portions of the Software.

-- THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
-- IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
-- FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
-- AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
-- LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
-- FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
-- DEALINGS IN THE SOFTWARE.
------------------------------------------------------------------------------

versioning =
  name: "Cycles.a"
  description: "Cycles tags on selected lines"
  version: "1.0.11"
  author: "Akatsumekusa and contributors"
  namespace: "aka.Cycles"
  requiredModules: "[{ \"moduleName\": \"a-mo.LineCollection\" }, { \"moduleName\": \"l0.ASSFoundation\" }, { \"moduleName\": \"aka.actor\" }, { \"moduleName\": \"aka.config\" }, { \"moduleName\": \"aka.outcome\" }]"

export script_name = versioning.name
export script_description = versioning.description
export script_version = versioning.version
export script_author = versioning.author
export script_namespace = versioning.namespace

DepCtrl = (require "l0.DependencyControl") {
  name: versioning.name,
  description: versioning.description,
  version: versioning.version,
  author: versioning.author,
  moduleName: versioning.namespace,
  url: "https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts",
  feed: "https://raw.githubusercontent.com/Akatmks/Akatsumekusa-Aegisub-Scripts/master/DependencyControl.json",
  {
    { "a-mo.LineCollection" },
    { "l0.ASSFoundation" },
    { "aka.actor" },
    { "aka.config" },
    { "aka.outcome" }
  }
}
LineCollection, ASS, aactor, aconfig, outcome = DepCtrl\requireModules!
ok = outcome.ok
err = outcome.err


  
aconfig = aconfig.make_editor
  display_name: "aka.Cycles"
  presets:
    "unanimated":
      "\\an": { 1, 2, 3, 4, 5, 6, 7, 8, 9 }
      "\\alpha": { "FF", "00", "10", "30", "60", "80", "A0", "C0", "E0" }
      "\\blur": { 0.6, 0.8, 1, 1.2, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 0.4, 0.5 }
      "\\bord": { 0, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 20 }
      "\\fsp": { 0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20, 30 }
      "\\shad": { 0, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 }
    "Akatsumekusa": 
      "\\alpha": { "00", "05", "0A", "10", "18", "20", "28", "30", "40", "50", "60", "70", "80", "88", "90", "98", "A0", "A8", "B0", "B8", "C0", "D0", "E0", "F0", "FF" }
      "\\blur": { 0.53, 0.56, 0.6, 0.65, 0.7, 0.8, 1, 1.2, 1.5, 1.7, 2, 2.5, 3, 4, 5, 6, 7, 10, 15, 20, 30, 0, 0.35, 0.4, 0.44, 0.47, 0.5 }
      "\\bord": { 0, 0.6, 0.8, 1, 1.2, 1.5, 1.7, 2, 2.2, 2.5, 2.7, 3, 3.2, 3.5, 4, 4.5, 5, 5.5, 6, 7.5, 9, 10.5, 12, 13.5, 15 }
      "\\shad": { 0, 0.7, 1, 1.2, 1.5, 1.7, 2, 2.2, 2.5, 2.7, 3, 3.2, 3.5, 3.7, 4, 4.2, 4.5, 4.7, 5, 5.2, 5.5, 5.7, 6, 6.5, 7, 7.5, 8, 9, 10.5, 12 }
  default: "unanimated"
validation_func = (config) ->
  all_number = (table_) ->
    for i, v in ipairs table_
      return err i unless (type v) == "number"
    return ok!

  all_hex = (table_) ->
    for i, v in ipairs table_
      return err i unless (type v) == "string"
      return err i unless tonumber(v, 16)
    return ok!
    
  msg = ""
  add_msg = (to_insert) ->
    if msg == ""
      msg = to_insert
    else
      msg ..= "\n" .. to_insert

  for k, v in pairs config
    if k == "\\an" or k == "\\bord" or k == "\\xbord" or k == "\\ybord" or k == "\\shad" or k == "\\xshad" or k == "\\yshad" or
       k == "\\fs" or k == "\\fsp" or k == "\\blur" or k == "\\be" or
       k == "\\frx" or k == "\\fry" or k == "\\frz" or k == "\\fax" or k == "\\fay" or k == "\\fscx" or k == "\\fscy"
      with all_number v
        \ifErr (i) ->
          add_msg "Invalid value in \"" .. k .. "\" at position " .. (tostring i)
    elseif k == "\\alpha" or k == "\\1a" or k == "\\2a" or k == "\\3a" or k == "\\4a"
      with all_hex v
        \ifErr (i) ->
          add_msg "Invalid value in \"" .. k .. "\" at position " .. (tostring i)
          add_msg "\talpha values are represented by a string of two chars from \'0\' to \'F\' in the config"
    else
      add_msg "Invalid key " .. (tostring k)
      add_msg "\tPossible keys include ASS tags that has a single numeric value and alphas"

  return ok config if msg == ""
  return err msg
local config

prepare_config = (config) ->
  for k, _ in pairs config
    if k == "\\alpha" or k == "\\1a" or k == "\\2a" or k == "\\3a" or k == "\\4a"
      for i, _ in ipairs config[k]
        if (type config[k][i]) == "string"
          config[k][i] = tonumber config[k][i], 16

    config[k].n = #config[k]
    config[k].min = 1
    for i = 1, config[k].n
      config[k][config[k].n + i] = config[k][i]
      if config[k][i] < config[k][config[k].min]
        config[k].min = i
    config[k][0] = config[k][config[k].n]

  return ok config

EditConfig = () ->
  with aconfig\read_edit_validate_and_save_config "aka.Cycles", validation_func
    with \ifErr aegisub.cancel
      with \andThen prepare_config
        config = \unwrap!



Cycles = (sub, sel, act, tag) ->
  if not config
    with aconfig\read_and_validate_config_if_empty_then_default_or_else_edit_and_save "aka.Cycles", validation_func
      with \ifErr aegisub.cancel
        with \andThen prepare_config
          config = \unwrap!
  if not config[tag]
    aegisub.debug.out "[aka.Cycles] No config found for \\" .. tag .. "\n"
    aegisub.debug.out "[aka.Cycles] To setup config for \\" .. tag .. ", click „Edit config“ and add a new line" .. "\n"
    aegisub.cancel()

  seq = config[tag]
  tag = ASS.toTagName[tag]


  lines = LineCollection sub, sel, () -> true
  for line in *lines
    data = ASS\parse line
    tags = (data\getEffectiveTags 1, false, false, false).tags

    if not tags[tag]
      data\insertTags ASS\createTag tag, seq[1]
    else
      (() ->
        set_next_after = (i) ->
          if not aactor.flag line, "switch"
            tags[tag]\set seq[i + 1]
          else
            tags[tag]\set seq[i - 1]

        set_next = (i) ->
          if not aactor.flag line, "switch"
            tags[tag]\set seq[i + 1]
          else
            tags[tag]\set seq[i]

        for i = 1, seq.n
          if tags[tag]\get! == seq[i]
            set_next_after i
            return

        if tags[tag]\get! < seq[seq.min] or
           tags[tag]\get! > seq[seq.min - 1]
          set_next seq.min - 1
          return
            
        for i = seq.min, seq.min + seq.n - 2
          if tags[tag]\get! > seq[i] and
             tags[tag]\get! < seq[i + 1]
            set_next i
            return
      )!
    data\commit!

  lines\replaceLines!

Switch = (sub, sel, act) ->
  lines = LineCollection sub, sel, () -> true
  for line in *lines
    aactor.toggleFlag line, "switch"

  lines\replaceLines!

  

Cycles_an    = (sub, sel, act) -> Cycles(sub, sel, act, "\\an"   )
Cycles_bord  = (sub, sel, act) -> Cycles(sub, sel, act, "\\bord" )
Cycles_xbord = (sub, sel, act) -> Cycles(sub, sel, act, "\\xbord")
Cycles_ybord = (sub, sel, act) -> Cycles(sub, sel, act, "\\ybord")
Cycles_shad  = (sub, sel, act) -> Cycles(sub, sel, act, "\\shad" )
Cycles_xshad = (sub, sel, act) -> Cycles(sub, sel, act, "\\xshad")
Cycles_yshad = (sub, sel, act) -> Cycles(sub, sel, act, "\\yshad")
Cycles_fs    = (sub, sel, act) -> Cycles(sub, sel, act, "\\fs"   )
Cycles_fsp   = (sub, sel, act) -> Cycles(sub, sel, act, "\\fsp"  )
Cycles_blur  = (sub, sel, act) -> Cycles(sub, sel, act, "\\blur" )
Cycles_be    = (sub, sel, act) -> Cycles(sub, sel, act, "\\be"   )
Cycles_frx   = (sub, sel, act) -> Cycles(sub, sel, act, "\\frx"  )
Cycles_fry   = (sub, sel, act) -> Cycles(sub, sel, act, "\\fry"  )
Cycles_frz   = (sub, sel, act) -> Cycles(sub, sel, act, "\\frz"  )
Cycles_fax   = (sub, sel, act) -> Cycles(sub, sel, act, "\\fax"  )
Cycles_fay   = (sub, sel, act) -> Cycles(sub, sel, act, "\\fay"  )
Cycles_fscx  = (sub, sel, act) -> Cycles(sub, sel, act, "\\fscx" )
Cycles_fscy  = (sub, sel, act) -> Cycles(sub, sel, act, "\\fscy" )
Cycles_alpha = (sub, sel, act) -> Cycles(sub, sel, act, "\\alpha")
Cycles_1a    = (sub, sel, act) -> Cycles(sub, sel, act, "\\1a"   )
Cycles_2a    = (sub, sel, act) -> Cycles(sub, sel, act, "\\2a"   )
Cycles_3a    = (sub, sel, act) -> Cycles(sub, sel, act, "\\3a"   )
Cycles_4a    = (sub, sel, act) -> Cycles(sub, sel, act, "\\4a"   )

DepCtrl\registerMacros {
  { "Cycle \\an"   , "Cycle \\an"   , Cycles_an    }
  { "Cycle \\bord" , "Cycle \\bord" , Cycles_bord  }
  { "Cycle \\xbord", "Cycle \\xbord", Cycles_xbord }
  { "Cycle \\ybord", "Cycle \\ybord", Cycles_ybord }
  { "Cycle \\shad" , "Cycle \\shad" , Cycles_shad  }
  { "Cycle \\xshad", "Cycle \\xshad", Cycles_xshad }
  { "Cycle \\yshad", "Cycle \\yshad", Cycles_yshad }
  { "Cycle \\fs"   , "Cycle \\fs"   , Cycles_fs    }
  { "Cycle \\fsp"  , "Cycle \\fsp"  , Cycles_fsp   }
  { "Cycle \\blur" , "Cycle \\blur" , Cycles_blur  }
  { "Cycle \\be"   , "Cycle \\be"   , Cycles_be    }
  { "Cycle \\frx"  , "Cycle \\frx"  , Cycles_frx   }
  { "Cycle \\fry"  , "Cycle \\fry"  , Cycles_fry   }
  { "Cycle \\frz"  , "Cycle \\frz"  , Cycles_frz   }
  { "Cycle \\fax"  , "Cycle \\fax"  , Cycles_fax   }
  { "Cycle \\fay"  , "Cycle \\fay"  , Cycles_fay   }
  { "Cycle \\fscx" , "Cycle \\fscx" , Cycles_fscx  }
  { "Cycle \\fscy" , "Cycle \\fscy" , Cycles_fscy  }
  { "Cycle \\alpha", "Cycle \\alpha", Cycles_alpha }
  { "Cycle \\1a"   , "Cycle \\1a"   , Cycles_1a    }
  { "Cycle \\2a"   , "Cycle \\2a"   , Cycles_2a    }
  { "Cycle \\3a"   , "Cycle \\3a"   , Cycles_3a    }
  { "Cycle \\4a"   , "Cycle \\4a"   , Cycles_4a    }
  { "Switch"       , "Switch cycles", Switch       }
  { "Edit config"  , "Edit config for aka.Cycles", EditConfig }
}
