# UAV ROUTE OPTIMIZER

### Instruction:

To run application you need to execute following command:
```bash python3 main.py```

#### You need to specify datasource for the program

1. To generate 5 (it could be another number) samples and run them add this flag:

```bash
--generate -n 5
```

2. To use existing file(s) add this flag:

```bash
--file
```

##### You can use only one datasource at once

#### You need specify which algorithms to use:

1. To use all algorithms use this flag:

```bash
--algorithms all
```

2. To use only greedy algorithm use this flag:

```bash
--algorithms greedy
```


2. To use only heuristic algorithm use this flag:

```bash
--algorithms heuristic
```



#### The examples of whole start command:

```bash
python3 main.py --algorithm all --file

python3 main.py --algorithm greedy --generate -n 5
```





