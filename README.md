# 编译运行过程

```bash
cd <project-root-dir>
gn gen out
ninja -C out hello
./out/hello
```

预期输出：
```
Hello from RUST
```

---

