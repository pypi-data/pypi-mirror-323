import os

_include_iteration_max_depth = 16

"""
Goal is to be able to run an 'eda' command, such as:
     > eda sim --target-packager <--stop-before-compile> \
               --tool verilator [--waves] [--dump-vcd] [other args] \
               <files or target>

Or a 'multi sim' command:
     > eda multi sim --target-packager <--stop-before-compile> \
               --tool verilator [--waves] [--dump-vcd] [other args] \
               <files or target wildcard>

And doing so would create:
   ./eda.work/<target>_sim/target_packager/
      ./DEPS.yml              -- new file with single target, all defines, incdirs, sources, top, etc.
      ./<all source files>    -- edited to flatten path information in `include
      ./<all `included files> -- edited to flatten path information in `include
      ./test.json             -- single file that can be as starting point for test runner service
                              -- Or a singular test.jsonl

A multi sim command would also create:
   ./eda.work/multi/tests.jsonl

And, we could re-run a single target in place as, but won't support this for 'multi sim':
  > cd ./eda.work/<target>_sim/target_packager/
  > eda sim test

`include problem:
1. In SystemVerilog, a `include "foo.svh", no tools allow you to add this to your compile/build
   flow via filename. They all do this per directory.
   -- As a result, we do not track includes, other than "incdirs" in our DEPS.yml tables.
   -- relative path or absolute path includes are allowed:
      - `include "../../../../usr/bin/foo.svh"
      - `include "deeper/path/lets/go/foo.svh"
2. Given a compile, we do not know the exact individual files were `include'd.
3. Verific will not tell us which files wer actually `include'd in $root scope (would tell us
   within the module scope).
4. WHY IS THIS A PROBLEM
   - If we do nothing, Frogger will be responible for creating all relative or absolute
     directories. I see this as a security risk and infeasible to implement.
     -- aka, Frogger runs a test in /
5. Solutions:
   a. One option is: we make a decision to not support path information in includes, and
      manage this only in DEPS.yml 'incdirs'.
      -- This may not be ideal for some hypothetical customer in the future.
         (If you want to use our tool and Frogger, refactor your code first!)
   b. Another option is - we support limited parsing in this "eda sim --target-packager" flow
      to copy + edit the file to strip path information in includes, so that Frogger can create
      all files in a single working directory.


*IF* we make the decision to only support `include w/out path information in
the opencos repo, and suggest that this is preferred, then <all * files> could
instead be symbolic links.
   ./eda.work/<target>_sim/target_packager/
      ./DEPS.yml              -- new file with single target, all defines, incdirs, sources, top, etc.
      ./<all source files>    -- as symbolic links
      ./<all `included files> -- as symbolic links
      ./test.json             -- single file that can be as starting point for test runner service


*IF* we want to support relative or absolute path based `include "../../foo.svh", then
we get to unravel that with a copied and edited file.
Looking in eth-puzzles/bin/create_tests_jsonl_eda.py, the first step is running (since we didn't
edit eda.py at all) effectively:

     > eda sim --stop-before-compile --tool verilator <some-target>

and examining the eda.work/some-target_sim/compile_only.sh file.# From there,
the commands are split and we figure out incdirs, defines, source files, top
module name and any other knobs.
We then get the full path information of every source file, and infer the 'top'
file if it was not set otherwise. Finally, we resolve the `include nightmare in
all source files, and check that they exist in the incdirs we know about.

** If a file has no `include, and no edits, it will be a symbolic link
** If a file had any edits, it will not be a symbolic link
** We must check that edited files only have affected diff lines on lines containing `include.


An example packaged DEPS.yml file:

test:
  multi:
    ignore:
      # This is required so that generated DEPS.yml files are not picked
      # up by future 'eda multi sim' commands.
      - commands: sim synth build
  tags:
    only-tools:
      # Note, tags are not fully supported by 'eda' yet, but if the
      # original command was spec'd for a verilator compile list, then
      # that should be the only tool supported.
      - verilator
  incdirs: .
  deps:
    - oclib_assert_pkg.sv
    - oclib_pkg.sv
    - oclib_memory_bist_pkg.sv
    - oclib_uart_pkg.sv
    - ocsim_pkg.sv
    - ocsim_packet_pkg.sv
    - ocsim_tb_control.sv
    - oclib_ram1rw.sv
    - oclib_ram1rw_test.sv
  top: oclib_ram1rw_test
  defines:
    LATENCY: 0


An example of a test.json file (w/out ## comments b/c json is a no comments zone):

  "name":    "oclib_am1rw_test",   ## This might match the DEPS.yml - <target>: top value.
                                   ## Drew would expect this to be the how I can identify my test
                                   ## when I want to look a logs, errors, artifacts

  "eda":     true,                 ## Must be true, Frogger will run this using 'eda'

  "eda_command": "eda sim --waves --tool verilator test",
                                   ## Command Frogger should expect to run
                                   ## If we find this to be gross or bad-security-practice
                                   ## then I'm not sure on the alterative. Frogger could
                                   ## be aware of allow-listed args that 'eda' suports, so
                                   ## Chip team putting its desired command in a json Array of
                                   ## args is not any different than a space separated string?
                                   ## recommand: mylist = shlex.split(eda_command)

  "eda_target": "test",            ## Name of the DEPS.yml <target>.
                                   ## Could instead use "tb_name" but this is Drew's preference.

  "tb": [
    {"name": "DEPS.yml",          "content": <string file contents> },
    {"name": oclib_assert_pkg.sv, "content": <string file contents> },
    ## ...
    {"name": oclib_ram1rw_test.sv, "content": <string file contents> },

    ## Note that this will match the same order in the Array in DEPS.yml <target>:deps value.
    ## This is the compile order.

    ## We will not pass other hidden information that Frogger has to deal with. Any
    ## 'defines' or 'incdirs' or other Verilator compile flags will be in the DEPS.yml.
  ],

  ## AI Team may have other exciting test runner Table key/value items. Drew has no use for:
  ## - canonical_dut, dut, query, prefix, top, tb_name (if I get "eda_target")

"""

def find_sv_included_files_within_file(filename:str, known_incdir_paths:list) -> list:

    found_included_files = set()
    ret = list()

    assert any(filename.endswith(x) for x in ['.v', '.sv', '.vh', '.svh']), \
        f'{filename=} does not have a supported extension, refusing to parse it'
    assert os.path.exists(filename), f'{filename=} does not exist'

    with open(filename) as f:

        for line in f.readlines():
            if '`include' in line:
                # strip comments on line, in case someone has: // `include "lib/foo.svh"
                # we can't handle /* comments */ on a line like this.
                assert '/*' not in line
                parts = line.split("//")
                words = parts[0].split() # only use what's on the left of the comments
                prev_word_is_tick_include = False
                ##print(f'(DEBUG): found `include in {line=} {parts=} {words=}')
                for word in words:
                    word = word.rstrip('\n')
                    if word == '`include':
                        # don't print this word, wait until next word
                        prev_word_is_tick_include = True
                        ##print(f'(DEBUG):    {word=}')
                    elif prev_word_is_tick_include:
                        assert word.startswith('"')
                        assert word.endswith('"')
                        prev_word_is_tick_include = False
                        include_fname = word[1:-1] # trim " at start and end
                        if include_fname not in found_included_files:
                            # this has path information, perhaps relative, perhaps absolute, or
                            # perhaps relative to any of the +incdir+ paths. Figure that out later.
                            found_included_files.add(include_fname)

    for fname in found_included_files:
        # Does this file exist, using our known_incdir_paths?
        for some_dir in known_incdir_paths:
            try_file_path = os.path.join(some_dir, fname)
            if os.path.exists(try_file_path) and try_file_path not in ret:
                ret.append(try_file_path)

        # TODO(drew): Warning if file doesn't exist, this would eventually result in a
        # compiler error.
        # TODO(drew): Warning if included file doesn't end  in .v, .sv, .vh, .svh.

    return ret



def get_list_sv_included_files(all_src_files:list, known_incdir_paths:list, target:str='') -> list:

    sv_included_files_dict = dict() # key, value is if we've traversed it (bool)

    # We now have to comb through all the tb_files (aka all src files including dut.sv)
    # so we can store them in an ordered file list for compiling.
    # We do have to go through all the src files looking for includes to flattend the path
    # information:
    #    `include "path/to/foo.s?vh" with
    # needs to become
    #    `include "foo.s?vh"
    # We also have to locate these files path/to/foo.s?vh" and add them to our source files
    # aka tb_files, b/c they were not otherwise in the list from eda's compile_only.sh

    # order shouldn't matter, these will get added to the testrunner's filelist and
    # be included with +incdir+.

    for fname in all_src_files:
        included_files_list = find_sv_included_files_within_file(
            filename=fname,
            known_incdir_paths=known_incdir_paths
        )

        for f in included_files_list:
            if f not in sv_included_files_dict:
                sv_included_files_dict[f] = False # add entry, mark it not traversed.

    for _ in range(_include_iteration_max_depth):
        # TODO(drew): consider doing this as a while not all(sv_included_files_dict.values())
        # (meaning one or more is false, aka not traversed)

        # do these for a few levels, in case `include'd file includes another file.
        # If we have more than 8 levels of `include hunting, then rethink this.
        for fname,traversed in sv_included_files_dict.items():
            if not traversed:
                included_files_list = find_sv_included_files_within_file(
                    filename=fname,
                    known_incdir_paths=known_incdir_paths
                )
                sv_included_files_dict[fname] = True # mark as traversed.

                for f in included_files_list:
                    if f not in sv_included_files_dict:
                        sv_included_files_dict[f] = False # add entry, mark it not traversed.

    ret = list()
    for fname,traversed in sv_included_files_dict.items():
        assert traversed, f'{fname=} has not been traversed, {sv_included_files_dict=} from {target=}'

        # add all the included files (should be traversed!) to our return list
        ret.append(fname)

    return ret
