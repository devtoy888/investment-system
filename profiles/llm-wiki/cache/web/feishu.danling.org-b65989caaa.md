[跳转至](https://feishu.danling.org/task/tasks/#feishu.task.tasks)

# tasks

## ``feishu.task.tasks [¶](https://feishu.danling.org/task/tasks/\#feishu.task.tasks "Permanent link")

### ``TasksNamespace [¶](https://feishu.danling.org/task/tasks/\#feishu.task.tasks.TasksNamespace "Permanent link")

Bases: `Namespace`

任务（Task）接口命名空间。

通过 `client.task.tasks` 访问，封装飞书任务 v2 中任务对象的增删改查。任务以 `task_guid` 唯一标识，
返回体中同时带有面向用户的 `task_id`（形如 `t100041`）与可直接打开的 `url`。

通常无需直接实例化，应通过 `client.task.tasks` 访问。

飞书文档

[创建任务](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/task-v2/task/create)

源代码位于： `feishu/task/tasks.py`

| Python |
| --- |
| ```<br> 34<br> 35<br> 36<br> 37<br> 38<br> 39<br> 40<br> 41<br> 42<br> 43<br> 44<br> 45<br> 46<br> 47<br> 48<br> 49<br> 50<br> 51<br> 52<br> 53<br> 54<br> 55<br> 56<br> 57<br> 58<br> 59<br> 60<br> 61<br> 62<br> 63<br> 64<br> 65<br> 66<br> 67<br> 68<br> 69<br> 70<br> 71<br> 72<br> 73<br> 74<br> 75<br> 76<br> 77<br> 78<br> 79<br> 80<br> 81<br> 82<br> 83<br> 84<br> 85<br> 86<br> 87<br> 88<br> 89<br> 90<br> 91<br> 92<br> 93<br> 94<br> 95<br> 96<br> 97<br> 98<br> 99<br>100<br>101<br>102<br>103<br>104<br>105<br>106<br>107<br>108<br>109<br>110<br>111<br>112<br>113<br>114<br>115<br>116<br>117<br>118<br>119<br>120<br>121<br>122<br>123<br>124<br>125<br>126<br>127<br>128<br>129<br>130<br>131<br>132<br>133<br>134<br>135<br>136<br>137<br>138<br>139<br>140<br>141<br>142<br>143<br>144<br>145<br>146<br>147<br>148<br>149<br>150<br>151<br>152<br>153<br>154<br>155<br>156<br>157<br>158<br>159<br>160<br>161<br>162<br>163<br>164<br>165<br>166<br>167<br>168<br>169<br>170<br>171<br>172<br>173<br>174<br>175<br>176<br>177<br>178<br>179<br>180<br>181<br>182<br>183<br>184<br>185<br>186<br>187<br>188<br>189<br>190<br>191<br>192<br>193<br>194<br>195<br>196<br>197<br>198<br>199<br>200<br>201<br>``` | ```<br>class TasksNamespace(Namespace):<br>    r"""<br>    任务（Task）接口命名空间。<br>    通过 `client.task.tasks` 访问，封装飞书任务 v2 中任务对象的增删改查。任务以 `task_guid` 唯一标识，<br>    返回体中同时带有面向用户的 `task_id`（形如 `t100041`）与可直接打开的 `url`。<br>    通常无需直接实例化，应通过 `client.task.tasks` 访问。<br>    飞书文档:<br>        [创建任务](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/task-v2/task/create)<br>    """<br>    async def create(self, task: dict[str, Any], *, user_id_type: str | None = None) -> NestedDict:<br>        r"""<br>        创建任务。<br>        将 `task` 作为请求体发送至创建任务接口。<br>        Args:<br>            task: 任务数据，原样作为 JSON 发送，常见键包括 `summary`（标题）、`description`、`due`（截止时间）、<br>                `members`（成员，含 `id`/`role`/`type`）、`start`、`tasklists` 等。<br>            user_id_type: 用户 ID 的类型，如 `open_id`、`union_id`、`user_id`；为空时使用接口默认值。<br>        Returns:<br>            创建结果数据，含 `task` 字段，内含 `guid`（任务唯一标识）、`task_id`、`summary`、`status`、<br>            `url`、`creator`、`created_at` 等信息。<br>        Raises:<br>            feishu.errors.FeishuError: 请求失败或返回错误码时抛出。<br>        飞书文档:<br>            [创建任务](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/task-v2/task/create)<br>        Examples:<br>            >>> await client.task.tasks.create({"summary": "写周报"})  # doctest:+SKIP<br>            {'task': {'guid': 'd116...', 'task_id': 't100041', 'summary': '写周报', 'status': 'todo'}}<br>        """<br>        params: dict[str, Any] = {}<br>        if user_id_type is not None:<br>            params["user_id_type"] = user_id_type<br>        return await self._request_data("POST", "task/v2/tasks", params=params, json=task)<br>    async def delete(self, task_guid: str) -> NestedDict:<br>        r"""<br>        删除任务。<br>        Args:<br>            task_guid: 任务唯一标识 `guid`。<br>        Returns:<br>            空数据体（接口成功时不返回额外字段）。<br>        Raises:<br>            feishu.errors.FeishuError: 请求失败或返回错误码时抛出。<br>        飞书文档:<br>            [删除任务](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/task-v2/task/delete)<br>        Examples:<br>            >>> await client.task.tasks.delete("d116...")  # doctest:+SKIP<br>            {}<br>        """<br>        return await self._request_data("DELETE", f"task/v2/tasks/{quote_segment(task_guid)}")<br>    async def get(self, task_guid: str, *, user_id_type: str | None = None) -> NestedDict:<br>        r"""<br>        获取任务详情。<br>        Args:<br>            task_guid: 任务唯一标识 `guid`。<br>            user_id_type: 用户 ID 的类型，如 `open_id`、`union_id`、`user_id`；为空时使用接口默认值。<br>        Returns:<br>            任务数据，含 `task` 字段（结构同 [`create`][feishu.task.tasks.TasksNamespace.create] 的返回）。<br>        Raises:<br>            feishu.errors.FeishuError: 请求失败或返回错误码时抛出。<br>        飞书文档:<br>            [获取任务详情](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/task-v2/task/get)<br>        Examples:<br>            >>> await client.task.tasks.get("d116...")  # doctest:+SKIP<br>            {'task': {'guid': 'd116...', 'summary': '写周报', 'status': 'todo'}}<br>        """<br>        params: dict[str, Any] = {}<br>        if user_id_type is not None:<br>            params["user_id_type"] = user_id_type<br>        return await self._request_data("GET", f"task/v2/tasks/{quote_segment(task_guid)}", params=params)<br>    async def list(<br>        self,<br>        *,<br>        completed: bool | None = None,<br>        user_id_type: str | None = None,<br>        page_size: int = 50,<br>        max_items: int | None = None,<br>    ) -> builtins.list[NestedDict]:<br>        r"""<br>        获取“我负责的任务”列表。<br>        自动翻页并汇总当前用户负责的任务。该接口仅支持以 `user_access_token` 调用。<br>        Args:<br>            completed: 是否只返回已完成（`True`）/ 未完成（`False`）的任务；为空时返回全部。<br>            user_id_type: 用户 ID 的类型，如 `open_id`、`union_id`、`user_id`；为空时使用接口默认值。<br>            page_size: 每页数量。默认为 50；超过 [feishu.consts.MAX_PAGE_SIZE][] 时由客户端收敛。<br>            max_items: 最多返回的任务数量，`None` 表示不限制。默认为 `None`。<br>        Returns:<br>            任务对象列表（`data.items`）；无任务时返回空列表。<br>        Raises:<br>            feishu.errors.FeishuError: 请求失败或返回错误码时抛出。<br>        飞书文档:<br>            [获取任务列表](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/task-v2/task/list)<br>        Examples:<br>            >>> await client.as_user("u-xxx").task.tasks.list(completed=False)  # doctest:+SKIP<br>            [{'guid': 'd116...', 'summary': '写周报', 'status': 'todo'}]<br>        """<br>        params: dict[str, Any] = {}<br>        if completed is not None:<br>            params["completed"] = completed<br>        if user_id_type is not None:<br>            params["user_id_type"] = user_id_type<br>        return await self._client.paginate_get("task/v2/tasks", params=params, page_size=page_size, max_items=max_items)<br>    async def update(<br>        self,<br>        task_guid: str,<br>        task: dict[str, Any],<br>        update_fields: Iterable[str],<br>        *,<br>        user_id_type: str | None = None,<br>    ) -> NestedDict:<br>        r"""<br>        更新任务。<br>        飞书任务更新采用“字段白名单”语义：`task` 携带新值，`update_fields` 显式列出本次要更新的字段名，<br>        未列出的字段保持不变。<br>        Args:<br>            task_guid: 任务唯一标识 `guid`。<br>            task: 携带新值的任务字段，原样作为 JSON 发送（键同 `create`）。<br>            update_fields: 本次需要更新的字段名集合，例如 `["summary", "due"]`。<br>            user_id_type: 用户 ID 的类型，如 `open_id`、`union_id`、`user_id`；为空时使用接口默认值。<br>        Returns:<br>            更新后的任务数据，含 `task` 字段。<br>        Raises:<br>            feishu.errors.FeishuError: 请求失败或返回错误码时抛出。<br>        飞书文档:<br>            [更新任务](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/task-v2/task/patch)<br>        Examples:<br>            >>> await client.task.tasks.update("d116...", {"summary": "写月报"}, ["summary"])  # doctest:+SKIP<br>            {'task': {'guid': 'd116...', 'summary': '写月报'}}<br>        """<br>        params: dict[str, Any] = {}<br>        if user_id_type is not None:<br>            params["user_id_type"] = user_id_type<br>        body = {"task": task, "update_fields": list(update_fields)}<br>        return await self._request_data("PATCH", f"task/v2/tasks/{quote_segment(task_guid)}", params=params, json=body)<br>``` |

#### ``create`async`[¶](https://feishu.danling.org/task/tasks/\#feishu.task.tasks.TasksNamespace.create "Permanent link")

Python

```
create(task: dict[str, Any], *, user_id_type: str | None = None) -> NestedDict
```

创建任务。

将 `task` 作为请求体发送至创建任务接口。

参数：

| 名称 | 类型 | 描述 | 默认 |
| --- | --- | --- | --- |
| ##### `task` [¶](https://feishu.danling.org/task/tasks/\#feishu.task.tasks.TasksNamespace.create(task) "Permanent link") | `dict[str, Any]` | 任务数据，原样作为 JSON 发送，常见键包括 `summary`（标题）、`description`、`due`（截止时间）、<br>`members`（成员，含 `id`/`role`/`type`）、`start`、`tasklists` 等。 | _必需_ |
| ##### `user_id_type` [¶](https://feishu.danling.org/task/tasks/\#feishu.task.tasks.TasksNamespace.create(user_id_type) "Permanent link") | `str | None` | 用户 ID 的类型，如 `open_id`、`union_id`、`user_id`；为空时使用接口默认值。 | `None` |

返回：

| 类型 | 描述 |
| --- | --- |
| `NestedDict` | 创建结果数据，含 `task` 字段，内含 `guid`（任务唯一标识）、`task_id`、`summary`、`status`、 |
| `NestedDict` | `url`、`creator`、`created_at` 等信息。 |

引发：

| 类型 | 描述 |
| --- | --- |
| `FeishuError` | 请求失败或返回错误码时抛出。 |

飞书文档

[创建任务](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/task-v2/task/create)

示例：

| Python Console Session |
| --- |
| ```<br>1<br>2<br>``` | ```<br>>>> await client.task.tasks.create({"summary": "写周报"})<br>{'task': {'guid': 'd116...', 'task_id': 't100041', 'summary': '写周报', 'status': 'todo'}}<br>``` |

源代码位于： `feishu/task/tasks.py`

| Python |
| --- |
| ```<br>47<br>48<br>49<br>50<br>51<br>52<br>53<br>54<br>55<br>56<br>57<br>58<br>59<br>60<br>61<br>62<br>63<br>64<br>65<br>66<br>67<br>68<br>69<br>70<br>71<br>72<br>73<br>74<br>75<br>``` | ```<br>async def create(self, task: dict[str, Any], *, user_id_type: str | None = None) -> NestedDict:<br>    r"""<br>    创建任务。<br>    将 `task` 作为请求体发送至创建任务接口。<br>    Args:<br>        task: 任务数据，原样作为 JSON 发送，常见键包括 `summary`（标题）、`description`、`due`（截止时间）、<br>            `members`（成员，含 `id`/`role`/`type`）、`start`、`tasklists` 等。<br>        user_id_type: 用户 ID 的类型，如 `open_id`、`union_id`、`user_id`；为空时使用接口默认值。<br>    Returns:<br>        创建结果数据，含 `task` 字段，内含 `guid`（任务唯一标识）、`task_id`、`summary`、`status`、<br>        `url`、`creator`、`created_at` 等信息。<br>    Raises:<br>        feishu.errors.FeishuError: 请求失败或返回错误码时抛出。<br>    飞书文档:<br>        [创建任务](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/task-v2/task/create)<br>    Examples:<br>        >>> await client.task.tasks.create({"summary": "写周报"})  # doctest:+SKIP<br>        {'task': {'guid': 'd116...', 'task_id': 't100041', 'summary': '写周报', 'status': 'todo'}}<br>    """<br>    params: dict[str, Any] = {}<br>    if user_id_type is not None:<br>        params["user_id_type"] = user_id_type<br>    return await self._request_data("POST", "task/v2/tasks", params=params, json=task)<br>``` |

#### ``delete`async`[¶](https://feishu.danling.org/task/tasks/\#feishu.task.tasks.TasksNamespace.delete "Permanent link")

Python

```
delete(task_guid: str) -> NestedDict
```

删除任务。

参数：

| 名称 | 类型 | 描述 | 默认 |
| --- | --- | --- | --- |
| ##### `task_guid` [¶](https://feishu.danling.org/task/tasks/\#feishu.task.tasks.TasksNamespace.delete(task_guid) "Permanent link") | `str` | 任务唯一标识 `guid`。 | _必需_ |

返回：

| 类型 | 描述 |
| --- | --- |
| `NestedDict` | 空数据体（接口成功时不返回额外字段）。 |

引发：

| 类型 | 描述 |
| --- | --- |
| `FeishuError` | 请求失败或返回错误码时抛出。 |

飞书文档

[删除任务](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/task-v2/task/delete)

示例：

| Python Console Session |
| --- |
| ```<br>1<br>2<br>``` | ```<br>>>> await client.task.tasks.delete("d116...")<br>{}<br>``` |

源代码位于： `feishu/task/tasks.py`

| Python |
| --- |
| ```<br>77<br>78<br>79<br>80<br>81<br>82<br>83<br>84<br>85<br>86<br>87<br>88<br>89<br>90<br>91<br>92<br>93<br>94<br>95<br>96<br>97<br>``` | ```<br>async def delete(self, task_guid: str) -> NestedDict:<br>    r"""<br>    删除任务。<br>    Args:<br>        task_guid: 任务唯一标识 `guid`。<br>    Returns:<br>        空数据体（接口成功时不返回额外字段）。<br>    Raises:<br>        feishu.errors.FeishuError: 请求失败或返回错误码时抛出。<br>    飞书文档:<br>        [删除任务](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/task-v2/task/delete)<br>    Examples:<br>        >>> await client.task.tasks.delete("d116...")  # doctest:+SKIP<br>        {}<br>    """<br>    return await self._request_data("DELETE", f"task/v2/tasks/{quote_segment(task_guid)}")<br>``` |

#### ``get`async`[¶](https://feishu.danling.org/task/tasks/\#feishu.task.tasks.TasksNamespace.get "Permanent link")

Python

```
get(task_guid: str, *, user_id_type: str | None = None) -> NestedDict
```

获取任务详情。

参数：

| 名称 | 类型 | 描述 | 默认 |
| --- | --- | --- | --- |
| ##### `task_guid` [¶](https://feishu.danling.org/task/tasks/\#feishu.task.tasks.TasksNamespace.get(task_guid) "Permanent link") | `str` | 任务唯一标识 `guid`。 | _必需_ |
| ##### `user_id_type` [¶](https://feishu.danling.org/task/tasks/\#feishu.task.tasks.TasksNamespace.get(user_id_type) "Permanent link") | `str | None` | 用户 ID 的类型，如 `open_id`、`union_id`、`user_id`；为空时使用接口默认值。 | `None` |

返回：

| 类型 | 描述 |
| --- | --- |
| `NestedDict` | 任务数据，含 `task` 字段（结构同 [`create`](https://feishu.danling.org/task/tasks/#feishu.task.tasks.TasksNamespace.create "<code class=\"doc-symbol doc-symbol-heading doc-symbol-method\"></code>            <span class=\"doc doc-object-name doc-function-name\">create</span>     <span class=\"doc doc-labels\">       <small class=\"doc doc-label doc-label-async\"><code>async</code></small>   </span>") 的返回）。 |

引发：

| 类型 | 描述 |
| --- | --- |
| `FeishuError` | 请求失败或返回错误码时抛出。 |

飞书文档

[获取任务详情](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/task-v2/task/get)

示例：

| Python Console Session |
| --- |
| ```<br>1<br>2<br>``` | ```<br>>>> await client.task.tasks.get("d116...")<br>{'task': {'guid': 'd116...', 'summary': '写周报', 'status': 'todo'}}<br>``` |

源代码位于： `feishu/task/tasks.py`

| Python |
| --- |
| ```<br> 99<br>100<br>101<br>102<br>103<br>104<br>105<br>106<br>107<br>108<br>109<br>110<br>111<br>112<br>113<br>114<br>115<br>116<br>117<br>118<br>119<br>120<br>121<br>122<br>123<br>``` | ```<br>async def get(self, task_guid: str, *, user_id_type: str | None = None) -> NestedDict:<br>    r"""<br>    获取任务详情。<br>    Args:<br>        task_guid: 任务唯一标识 `guid`。<br>        user_id_type: 用户 ID 的类型，如 `open_id`、`union_id`、`user_id`；为空时使用接口默认值。<br>    Returns:<br>        任务数据，含 `task` 字段（结构同 [`create`][feishu.task.tasks.TasksNamespace.create] 的返回）。<br>    Raises:<br>        feishu.errors.FeishuError: 请求失败或返回错误码时抛出。<br>    飞书文档:<br>        [获取任务详情](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/task-v2/task/get)<br>    Examples:<br>        >>> await client.task.tasks.get("d116...")  # doctest:+SKIP<br>        {'task': {'guid': 'd116...', 'summary': '写周报', 'status': 'todo'}}<br>    """<br>    params: dict[str, Any] = {}<br>    if user_id_type is not None:<br>        params["user_id_type"] = user_id_type<br>    return await self._request_data("GET", f"task/v2/tasks/{quote_segment(task_guid)}", params=params)<br>``` |

#### ``list`async`[¶](https://feishu.danling.org/task/tasks/\#feishu.task.tasks.TasksNamespace.list "Permanent link")

Python

```
list(*, completed: bool | None = None, user_id_type: str | None = None, page_size: int = 50, max_items: int | None = None) -> list[NestedDict]
```

获取“我负责的任务”列表。

自动翻页并汇总当前用户负责的任务。该接口仅支持以 `user_access_token` 调用。

参数：

| 名称 | 类型 | 描述 | 默认 |
| --- | --- | --- | --- |
| ##### `completed` [¶](https://feishu.danling.org/task/tasks/\#feishu.task.tasks.TasksNamespace.list(completed) "Permanent link") | `bool | None` | 是否只返回已完成（`True`）/ 未完成（`False`）的任务；为空时返回全部。 | `None` |
| ##### `user_id_type` [¶](https://feishu.danling.org/task/tasks/\#feishu.task.tasks.TasksNamespace.list(user_id_type) "Permanent link") | `str | None` | 用户 ID 的类型，如 `open_id`、`union_id`、`user_id`；为空时使用接口默认值。 | `None` |
| ##### `page_size` [¶](https://feishu.danling.org/task/tasks/\#feishu.task.tasks.TasksNamespace.list(page_size) "Permanent link") | `int` | 每页数量。默认为 50；超过 [feishu.consts.MAX\_PAGE\_SIZE](https://feishu.danling.org/consts/#feishu.consts.MAX_PAGE_SIZE "<code class=\"doc-symbol doc-symbol-heading doc-symbol-attribute\"></code>            <span class=\"doc doc-object-name doc-attribute-name\">MAX_PAGE_SIZE</span>     <span class=\"doc doc-labels\">       <small class=\"doc doc-label doc-label-module-attribute\"><code>module-attribute</code></small>   </span>") 时由客户端收敛。 | `50` |
| ##### `max_items` [¶](https://feishu.danling.org/task/tasks/\#feishu.task.tasks.TasksNamespace.list(max_items) "Permanent link") | `int | None` | 最多返回的任务数量，`None` 表示不限制。默认为 `None`。 | `None` |

返回：

| 类型 | 描述 |
| --- | --- |
| `list[NestedDict]` | 任务对象列表（`data.items`）；无任务时返回空列表。 |

引发：

| 类型 | 描述 |
| --- | --- |
| `FeishuError` | 请求失败或返回错误码时抛出。 |

飞书文档

[获取任务列表](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/task-v2/task/list)

示例：

| Python Console Session |
| --- |
| ```<br>1<br>2<br>``` | ```<br>>>> await client.as_user("u-xxx").task.tasks.list(completed=False)<br>[{'guid': 'd116...', 'summary': '写周报', 'status': 'todo'}]<br>``` |

源代码位于： `feishu/task/tasks.py`

| Python |
| --- |
| ```<br>125<br>126<br>127<br>128<br>129<br>130<br>131<br>132<br>133<br>134<br>135<br>136<br>137<br>138<br>139<br>140<br>141<br>142<br>143<br>144<br>145<br>146<br>147<br>148<br>149<br>150<br>151<br>152<br>153<br>154<br>155<br>156<br>157<br>158<br>159<br>160<br>161<br>162<br>``` | ```<br>async def list(<br>    self,<br>    *,<br>    completed: bool | None = None,<br>    user_id_type: str | None = None,<br>    page_size: int = 50,<br>    max_items: int | None = None,<br>) -> builtins.list[NestedDict]:<br>    r"""<br>    获取“我负责的任务”列表。<br>    自动翻页并汇总当前用户负责的任务。该接口仅支持以 `user_access_token` 调用。<br>    Args:<br>        completed: 是否只返回已完成（`True`）/ 未完成（`False`）的任务；为空时返回全部。<br>        user_id_type: 用户 ID 的类型，如 `open_id`、`union_id`、`user_id`；为空时使用接口默认值。<br>        page_size: 每页数量。默认为 50；超过 [feishu.consts.MAX_PAGE_SIZE][] 时由客户端收敛。<br>        max_items: 最多返回的任务数量，`None` 表示不限制。默认为 `None`。<br>    Returns:<br>        任务对象列表（`data.items`）；无任务时返回空列表。<br>    Raises:<br>        feishu.errors.FeishuError: 请求失败或返回错误码时抛出。<br>    飞书文档:<br>        [获取任务列表](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/task-v2/task/list)<br>    Examples:<br>        >>> await client.as_user("u-xxx").task.tasks.list(completed=False)  # doctest:+SKIP<br>        [{'guid': 'd116...', 'summary': '写周报', 'status': 'todo'}]<br>    """<br>    params: dict[str, Any] = {}<br>    if completed is not None:<br>        params["completed"] = completed<br>    if user_id_type is not None:<br>        params["user_id_type"] = user_id_type<br>    return await self._client.paginate_get("task/v2/tasks", params=params, page_size=page_size, max_items=max_items)<br>``` |

#### ``update`async`[¶](https://feishu.danling.org/task/tasks/\#feishu.task.tasks.TasksNamespace.update "Permanent link")

Python

```
update(task_guid: str, task: dict[str, Any], update_fields: Iterable[str], *, user_id_type: str | None = None) -> NestedDict
```

更新任务。

飞书任务更新采用“字段白名单”语义：`task` 携带新值，`update_fields` 显式列出本次要更新的字段名，
未列出的字段保持不变。

参数：

| 名称 | 类型 | 描述 | 默认 |
| --- | --- | --- | --- |
| ##### `task_guid` [¶](https://feishu.danling.org/task/tasks/\#feishu.task.tasks.TasksNamespace.update(task_guid) "Permanent link") | `str` | 任务唯一标识 `guid`。 | _必需_ |
| ##### `task` [¶](https://feishu.danling.org/task/tasks/\#feishu.task.tasks.TasksNamespace.update(task) "Permanent link") | `dict[str, Any]` | 携带新值的任务字段，原样作为 JSON 发送（键同 `create`）。 | _必需_ |
| ##### `update_fields` [¶](https://feishu.danling.org/task/tasks/\#feishu.task.tasks.TasksNamespace.update(update_fields) "Permanent link") | `Iterable[str]` | 本次需要更新的字段名集合，例如 `["summary", "due"]`。 | _必需_ |
| ##### `user_id_type` [¶](https://feishu.danling.org/task/tasks/\#feishu.task.tasks.TasksNamespace.update(user_id_type) "Permanent link") | `str | None` | 用户 ID 的类型，如 `open_id`、`union_id`、`user_id`；为空时使用接口默认值。 | `None` |

返回：

| 类型 | 描述 |
| --- | --- |
| `NestedDict` | 更新后的任务数据，含 `task` 字段。 |

引发：

| 类型 | 描述 |
| --- | --- |
| `FeishuError` | 请求失败或返回错误码时抛出。 |

飞书文档

[更新任务](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/task-v2/task/patch)

示例：

| Python Console Session |
| --- |
| ```<br>1<br>2<br>``` | ```<br>>>> await client.task.tasks.update("d116...", {"summary": "写月报"}, ["summary"])<br>{'task': {'guid': 'd116...', 'summary': '写月报'}}<br>``` |

源代码位于： `feishu/task/tasks.py`

| Python |
| --- |
| ```<br>164<br>165<br>166<br>167<br>168<br>169<br>170<br>171<br>172<br>173<br>174<br>175<br>176<br>177<br>178<br>179<br>180<br>181<br>182<br>183<br>184<br>185<br>186<br>187<br>188<br>189<br>190<br>191<br>192<br>193<br>194<br>195<br>196<br>197<br>198<br>199<br>200<br>201<br>``` | ```<br>async def update(<br>    self,<br>    task_guid: str,<br>    task: dict[str, Any],<br>    update_fields: Iterable[str],<br>    *,<br>    user_id_type: str | None = None,<br>) -> NestedDict:<br>    r"""<br>    更新任务。<br>    飞书任务更新采用“字段白名单”语义：`task` 携带新值，`update_fields` 显式列出本次要更新的字段名，<br>    未列出的字段保持不变。<br>    Args:<br>        task_guid: 任务唯一标识 `guid`。<br>        task: 携带新值的任务字段，原样作为 JSON 发送（键同 `create`）。<br>        update_fields: 本次需要更新的字段名集合，例如 `["summary", "due"]`。<br>        user_id_type: 用户 ID 的类型，如 `open_id`、`union_id`、`user_id`；为空时使用接口默认值。<br>    Returns:<br>        更新后的任务数据，含 `task` 字段。<br>    Raises:<br>        feishu.errors.FeishuError: 请求失败或返回错误码时抛出。<br>    飞书文档:<br>        [更新任务](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/task-v2/task/patch)<br>    Examples:<br>        >>> await client.task.tasks.update("d116...", {"summary": "写月报"}, ["summary"])  # doctest:+SKIP<br>        {'task': {'guid': 'd116...', 'summary': '写月报'}}<br>    """<br>    params: dict[str, Any] = {}<br>    if user_id_type is not None:<br>        params["user_id_type"] = user_id_type<br>    body = {"task": task, "update_fields": list(update_fields)}<br>    return await self._request_data("PATCH", f"task/v2/tasks/{quote_segment(task_guid)}", params=params, json=body)<br>``` |

回到页面顶部