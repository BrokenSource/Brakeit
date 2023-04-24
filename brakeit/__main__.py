#!/usr/bin/env python3

import os
import subprocess

from pathlib import Path
import pygit2

BROKENSOURCE_REPO = "https://github.com/BrokenSource/BrokenSource"

def getBrokenSourceMonorepo():

    # Not the most pretty progress bar but it does the job
    class GitCloneProgress(pygit2.RemoteCallbacks):
        def transfer_progress(self, stats):
            print(f"\r:: Progress: ({stats.received_bytes} bytes) ({stats.indexed_objects}/{stats.total_objects} objects)", end='', flush=True)

    if Path("BrokenSource").exists():
        print("BrokenSource folder already exists on current directory. See instructions on Readme.md")
        return

    print("Cloning [BrokenSource/BrokenSource]")
    brokenSourceRepo = pygit2.clone_repository(BROKENSOURCE_REPO, "BrokenSource", callbacks=GitCloneProgress())
    os.chdir("BrokenSource")
    print("\n")

    # # Attempt to init and clone public submodules
    for submodule in brokenSourceRepo.listall_submodules():
        try:
            brokenSourceRepo.init_submodules([submodule])
            print(f"Cloning [BrokenSource/{submodule}]")
            brokenSourceRepo.update_submodules([submodule], callbacks=GitCloneProgress())

            # Open submodule as a repository, checkout Master branch
            submoduleRepo = pygit2.Repository(submodule)
            submoduleRepo.checkout(submoduleRepo.lookup_branch("Master"))
            print("\n")

        # Ignore private submodules
        except Exception as error:
            if "authentication" not in str(error):
                raise error
            print(":: Private repository\n")

    # Install dependencies on python venv
    subprocess.run(["python", "-m", "poetry", "install"])
    subprocess.run(["python", "-m", "poetry", "shell"])

if __name__ == "__main__":
    getBrokenSourceMonorepo()
