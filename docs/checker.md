# checker.py

**TODO: needs to be updated**

## Commands

```txt
--challenges
--categories
--flags
--handouts
--check
--run
--test
```

### Challenges

Lists all challenges present in the repository.

### Categories

Lists all main and sub categories present in the repository.

### flags

Lists all flags for all challenges present in the repository.

### Handouts

Lists all handouts for all relevant challenges present in the repository.

### Check

Ensures all challenges are properly formatted.

### Run

Takes an optional argument, if present it attempts to run a challenge by this name. If none is found the command
fails, if the challenge is found and successfully started it returns a connection string to the challenge.

If no arguments are present it attempts to run all challenges. No connection string is given in this case.

When running the challenges the port range `4000-4999` will be used to allocate ports to each challenge. The order
of port allocation is done sequentially, sorted by uuid.

### Test

Exact same syntax as the `Run` command, however it will run tests on the provided challenge. If this no challenge
is specified all challenges will be tested. The results will be written to STDOUT.
