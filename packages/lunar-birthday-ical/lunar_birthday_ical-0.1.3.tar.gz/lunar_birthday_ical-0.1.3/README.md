# lunar-birthday-ical

## 这是什么?

一个使用 Python 3 编写的用于创建农历生日事件的命令行工具.

`lunar-birthday-ical` 读入一个 YAML 配置文件, 生成 iCalendar 格式的 `.ics` 文件, 可选是否将日历上传到 pastebin, 方便直接订阅,
示例配置文件请参考 [config/example-lunar-birthday.yaml](config/example-lunar-birthday.yaml), 注释应该足够能解释每个选项分别是什么含义.

可以使用 `-h` 或者 `--help` 选项查看命令行工具帮助信息,

```
$ lunar-birthday-ical -h
usage: lunar-birthday-ical [-h] [-o OUTPUT] input

Generate iCal events for lunar birthday and cycle days.

positional arguments:
  input                 input config.yaml, check config/example-lunar-birthday.yaml for example.

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Path to save the generated iCal file.
```

## 安装

推荐使用 [`pipx`](https://github.com/pypa/pipx) 来安装 Python 编写的命令行工具, 包括本项目,

```ShellSession
$ pipx install lunar-birthday-ical
  installed package lunar-birthday-ical {{ version }}, installed using Python 3.11.2
  These apps are now globally available
    - lunar-birthday-ical
done! ✨ 🌟 ✨

$ lunar-birthday-ical config/example-lunar-birthday.yaml
[2025-01-25 12:17:05,137][lunar_birthday_ical.ical][INFO] iCal file saved to config/example-lunar-birthday.ics
```

## 关于 pastebin

在 YAML 配置文件中可选配置是否同时将生成的 `.ics` 文件同时上传 pastebin, 该 pastebin 实例是作者运行的一个基于 Cloudflare worker 的 pastebin 服务, 实例所使用的代码是 [SharzyL/pastebin-worker](https://github.com/SharzyL/pastebin-worker).

如果选择开启 `global.pastebin`, 在初次执行时, 可以保持 YAML 配置文件中的 `global.pastebin_name` 和 `global.pastebin_password` 为空, 命令执行时会自动上传, 上传成功后可以将标准输出中 `lunar_birthday_ical.pastebin` 日志行的 admin URL 中由 `:` 分隔的 `{{ pastebin_name }}` 和 `{{ pastebin_password }}` 手动填入配置文件, 这样下次再执行时就只会在原本的 URL 上更新, 而不会重新上传, 保持 URL 不变, 避免需要更新订阅日历的链接.

下方为开启 `global.pastebin` 后的命令行输出,

```ShellSession
$ lunar-birthday-ical config/example-lunar-birthday.yaml
[2025-01-25 12:17:05,137][lunar_birthday_ical.ical][INFO] iCal file saved to config/example-lunar-birthday.ics
[2025-01-25 12:17:07,040][httpx][INFO] HTTP Request: POST https://komj.uk/ "HTTP/1.1 200 OK"
[2025-01-25 12:17:07,041][lunar_birthday_ical.pastebin][INFO] {'url': 'https://komj.uk/{{ pastebin_name }}', 'suggestUrl': 'https://komj.uk/{{ pastebin_name }}/example-lunar-birthday.ics', 'admin': 'https://komj.uk/{{ pastebin_name }}:{{ pastebin_password }}', 'isPrivate': True, 'expire': None}
```
