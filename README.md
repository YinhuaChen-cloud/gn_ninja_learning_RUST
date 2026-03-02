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

# 显示某个 gn 目标使用到的所有 .rs 文件

命令如下：
```bash
gn desc out //:hello sources --format=json
```

显示如下：
```
{
   "//:hello": {
      "sources": [ "//main.rs", "//print.rs" ]
   }
}
```

---

# 让 rust-analyzer 解析 GN/Ninja

先生成 `rust-project.json`：

```bash
python3 scripts/gen_rust_project.py --out-dir out --target //:hello
```

然后在 VS Code 里重启 rust-analyzer（`Rust Analyzer: Restart Server`）。

当你在 `BUILD.gn` 中新增/删除 `.rs` 文件后，重新执行上面的脚本即可同步导航索引。

---
