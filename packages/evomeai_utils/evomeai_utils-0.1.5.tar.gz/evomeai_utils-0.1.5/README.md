This is a utils package 

## EConifig
a normal ini config class

## LogTimer
a multi-thread safe Time record class, used to calculte timecost of code blocks

```
with LogTimer('step1'):
    step1_func()

with LogTimer("step2_async"):
    Thread(target=step2_async_func, args=('D',)).start()
   
print(LogTimer.output())
```