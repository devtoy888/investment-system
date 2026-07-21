- [Home](https://open.larksuite.com/document/home/index)
- [Developer Guides](https://open.larksuite.com/document/client-docs/intro)
- [Server API](https://open.larksuite.com/document/server-docs/getting-started/getting-started)
- [Client API](https://open.larksuite.com/document/client-docs/h5/)
- [Lark CLI](https://open.larksuite.com/document/mcp_open_tools/overview-of-lark-agent-integration-capabilities)
- [Lark Plugin for OpenClaw](https://lark-technologies.larksuite.com/wiki/I1PEw40PJi8mbMkLdIJuk9Pasne)

API Explorer [CardKit](https://open.larksuite.com/tool/cardbuilder?from=open_docs_header)

Search content

Platform Introduction

Develop Process

Quick Starts

Develop Bots

Develop Web Apps

Develop Gadgets (Not Recommended)

Develop Docs Add-ons

Develop Base Extensions

Develop Workplace Blocks

Development link preview

Message cards

[Introduction of Message cards](https://open.larksuite.com/document/common-capabilities/message-card/introduction-of-message-cards)

[Overview of message card builder](https://open.larksuite.com/document/ukTMukTMukTM/uYzM3QjL2MzN04iNzcDN/message-card-builder)

Quick Start

Component

Build card with JSON

[Card JSON v2.0 breaking changes & release notes](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-breaking-changes-release-notes)

[Card JSON 2.0 structure](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-structure)

Card JSON 2.0 version components

[component JSON v2.0 overview](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/component-json-v2-overview)

containers

Display components

[Title](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/title)

[Plain text](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/plain-text)

[Rich text (Markdown)](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/rich-text)

[Image](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/image)

[Multi image laylout](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/multi-image-laylout)

[Divider](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/divider)

[User profile](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/user-profile)

[User list](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/user-list)

[Chart](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/chart)

[Table](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/table)

Interactive components

[Card JSON 1.0 structure](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-structure)

Card JSON 1.0 version components

[Configure multi-language content](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/configure-multi-language-content)

Build card content

Configuring card callbacks

[Preview and publish cards](https://open.larksuite.com/document/ukTMukTMukTM/uYzM3QjL2MzN04iNzcDN/preview-and-save-cards)

Send message card

[Update Feishu card](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/update-feishu-card)

Resources

Message Card Example

SSO&End User Consent

AppLink Protocol

Tools and SDKs

FAQ

Management Practice

Platform Notices

Deprecated Guides

Configure App Entry

[Developer Guides](https://open.larksuite.com/document/client-docs/intro) [Message cards](https://open.larksuite.com/document/common-capabilities/message-card/introduction-of-message-cards) [Build card with JSON](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-breaking-changes-release-notes) [Card JSON 2.0 version components](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/component-json-v2-overview) [Display components](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/title)

Rich text (Markdown)

# Rich text (Markdown)

Copy Page

Last updated on 2025-06-27

The contents of this article

[Notes](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/rich-text#0ff01b6a "Notes")

[Component properties](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/rich-text#1e2dc47b "Component properties")

[JSON structure](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/rich-text#3282a63a "JSON structure")

[Field descriptions](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/rich-text#622dac8e "Field descriptions")

[Demo example](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/rich-text#3f705c44 "Demo example")

[Supported Markdown syntax](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/rich-text#3dcaec43 "Supported Markdown syntax")

[Explanation of special character escaping](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/rich-text#6fb8622f "Explanation of special character escaping")

[Programming languages supported by code blocks](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/rich-text#7258688d "Programming languages supported by code blocks")

[Defining Different Font Sizes for Mobile and Desktop](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/rich-text#884a5e5d "Defining Different Font Sizes for Mobile and Desktop")

# Rich Text Component

The rich text (Markdown) component of the card supports rendering text, images, split lines, and other elements.

This document introduces the JSON 2.0 structure of the rich text component. To view the historical JSON 1.0 structure, refer to [Rich Text (Markdown)](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-components/content-components/rich-text).

## Notes

The rich text JSON 2.0 structure no longer supports the following differentiated jump syntax. You can use the link syntax with an icon (`<link></link>`) as a replacement, such as:`<link icon='chat_outlined' url='https://applink.larksuite.com/client/chat/xxxxx' pc_url='' ios_url='' android_url=''>Strategy Seminar</link>`.

```

{
 "tag": "markdown",
 "href": {
  "urlVal": {
   "url": "xxx",
   "pc_url":"xxx",
   "ios_url": "xxx",
   "android_url": "xxx"
   }
  },
 "content":
 "[Differentiated Jump]($urlVal)"
}
```

## Component properties

### JSON structure

The complete JSON 2.0 structure of the rich text component is as follows:

```

{
  "schema": "2.0", // The version of the card JSON structure. Default is 1.0. To use the JSON 2.0 structure, you must explicitly declare 2.0.
  "body": {
    "elements": [\
      {\
        "tag": "markdown",\
        "element_id": "custom_id", // The unique identifier for the operation component. New attribute in JSON 2.0. Used to specify the component in the related interface call. Customizable by the developer.\
        "margin": "0px 0px 0px 0px", // The margin of the component, new attribute in JSON 2.0. Default value is "0", supported range is [-99,99]px.\
        "content": "Personnel<person id = 'ou_449b53ad6aee526f7ed311b216aabcef' show_name = true show_avatar = true style = 'normal'></person>", // Content written in markdown syntax. The 2.0 structure no longer supports the "[Differentiated Jump]($urlVal)" syntax.\
        "text_size": "normal", // Text size. Default value is normal. Supports customization of different font sizes on mobile and desktop.\
        "text_align": "left", // Text alignment. Default value is left.\
        "icon": {\
          // Prefix icon.\
          "tag": "standard_icon", // Icon type.\
          "token": "chat-forbidden_outlined", // The token of the icon. Only effective when the tag is standard_icon.\
          "color": "orange", // Icon color. Only effective when the tag is standard_icon.\
          "img_key": "img_v2_38811724" // The key of the image. Only effective when the tag is custom_icon.\
        }\
      }\
    ]
  }
}
```

### Field descriptions

The parameter descriptions contained in the rich text component are shown in the following table.

| Field Name | Required | Type | Default Value | Description |
| --- | --- | --- | --- | --- |
| tag | Yes | String | / | The tag of the component. For the rich text component, it is fixed to `markdown`. |
| element\_id | No | String | Empty | The unique identifier for the operation component. New attribute in JSON 2.0. Used to specify the component in the [component-related interface](https://open.larksuite.com/document/uAjLw4CM/ukTMukTMukTM/cardkit-v1/card-element/create) call. The value of this field must be globally unique within the same card. Only letters, numbers, and underscores are allowed, must start with a letter, and cannot exceed 20 characters. |
| margin | No | String | 0 | The margin of the component. New attribute in JSON 2.0. The value range is \[-99,99\]px. Optional values:<br>- Single value, such as "10px", indicates that all four margins of the component are 10px.<br>- Double value, such as "4px 0", indicates that the top and bottom margins of the component are 4px, and the left and right margins are 0px. Separated by space (unit can be omitted when margin is 0).<br>- Multiple values, such as "4px 0 4px 0", indicate that the top, right, bottom, and left margins of the component are 4px, 12px, 4px, and 12px respectively. Separated by space. |
| text\_align | No | String | left | Sets the text alignment. Possible values are:<br>- left: left-aligned<br>- center: center-aligned<br>- right: right-aligned |
| text\_size | No | String | normal | Text size. Available values are as follows. If you enter other values, the card will display the font size corresponding to the `normal` field.<br>- heading-0: Extra large title (30px)<br>- heading-1: First level title (24px)<br>- heading-2: Second level title (20px)<br>- heading-3: Third level title (18px)<br>- heading-4: Fourth level title (16px)<br>- heading: Title (16px)<br>- normal: Body text (14px)<br>- notation: Auxiliary information (12px)<br>- xxxx-large: 30px<br>- xxx-large: 24px<br>- xx-large: 20px<br>- x-large: 18px<br>- large: 16px<br>- medium: 14px<br>- small: 12px<br>- x-small: 10px |
| icon | No | Object | / | Add an icon as a text prefix. Supports custom or icon library usage. |
| └ tag | No | String | / | Icon type label. Possible values:<br>- `standard_icon`: Use an icon from the icon library.<br>- `custom_icon`: Use a custom image as the icon. |
| └ token | No | String | / | The token of the icon from the icon library. Effective when `tag` is `standard_icon`. See enumeration values in [Icon Library](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/enumerations-for-icons). |
| └ color | No | String | / | The color of the icon. Supports setting colors for line and surface icons (i.e., tokens ending in `outlined` or `filled`). Effective when `tag` is `standard_icon`. See enumeration values in [Color Enumeration](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/enumerations-for-fields-related-to-color). |
| └ img\_key | No | String | / | The image key for a custom prefix icon. Effective when `tag` is `custom_icon`.<br>To obtain the icon key: Call the [Upload Image](https://open.larksuite.com/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/image/create) API, upload an image for messaging, and retrieve the image key from the response. |
| content | Yes | String | / | Markdown text content. For supported syntax, refer to the section below. |

### Demo example

The following example code of the JSON 2.0 structure can achieve the card effect as shown in the figure below:

![](https://sf16-sg.larksuitecdn.com/obj/open-platform-opendoc-sg/e8b73582a4505b5d1e4b0a707aa41aa6_7srlrpdZna.png?height=653&lazyload=true&maxWidth=300&width=614)

````

{
  "schema": "2.0",
  "body": {
    "elements": [\
      {\
        "tag": "markdown",\
        "content": "# 一级标题",\
        "margin": "0px 0px 0px 0px",\
        "text_align": "left",\
        "text_size": "normal"\
      },\
      {\
        "tag": "markdown",\
        "content": "标准emoji 😁😢🌞💼🏆❌✅\nLarkemoji :OK::THUMBSUP:\n*斜体* **粗体** ~~删除线~~ \n<font color='red'>这是红色文本<\/font>\n<text_tag color=\"blue\">标签<\/text_tag>\n[文字链接](https:\/\/open.feishu.cn\/document\/server-docs\/im-v1\/message-reaction\/emojis-introduce)\n<link icon='chat_outlined' url='https:\/\/open.feishu.cn' pc_url='' ios_url='' android_url=''>带图标的链接<\/link>\n<at id=all><\/at>\n- 无序列表1\n    - 无序列表 1.1\n- 无序列表2\n1. 有序列表1\n    1. 有序列表 1.1\n2. 有序列表2\n```JSON\n{\"This is\": \"JSON demo\"}\n```"\
      },\
      {\
        "tag": "markdown",\
        "content": "行内引用`code`"\
      },\
      {\
        "tag": "markdown",\
        "content": "数字角标，支持 1-99 数字<number_tag background_color='grey' font_color='white' url='https://open.larksuite.com'  pc_url='https://open.larksuite.com' android_url='https://open.larksuite.com' ios_url='https://open.larksuite.com'>1</number_tag>"\
      },\
      {\
        "tag": "markdown",\
        "content": "默认数字角标展示<number_tag>1</number_tag>"\
      },\
      {\
        "tag": "markdown",\
        "content": "人员<person id = 'ou_449b53ad6aee526f7ed311b216a8f88f' show_name = true show_avatar = true style = 'normal'></person>"\
      },\
      {\
        "tag": "markdown",\
        "content": "> 这是一段引用文字\n引用内换行 \n"\
      }\
    ]
  }
}
````

## Supported Markdown syntax

[Card JSON 2.0 structure](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-structure) supports all standard Markdown syntax and some HTML syntax except for `HTMLBlock`. To learn about the standard Markdown syntax, please refer to the [CommonMark Spec official documentation](https://spec.commonmark.org/0.31.2/). You can also use the [CommonMark playground](https://spec.commonmark.org/dingus/) to preview Markdown effects.

Note that in the rich text component of the card, the rendering effects of the following syntax differ from CommonMark:

- The rich text component supports using one Enter key as a soft break; two Enter keys as a hard break. Soft breaks may be ignored during rendering, depending on how the renderer handles them; hard breaks will always render as a new line.

- The 2.0 structure supports the following HTML syntax:

  - Opening tag `<br>`
  - Self-closing tag `<br/>`
  - Opening tag `<hr>`
  - Self-closing tag `<hr/>`
  - Closing tag `<person></person>`
  - Closing tag `<local_datetime></local_datetime>`
  - Closing tag `<at></at>`
  - Closing tag `<a></a>`
  - Closing tag `<text_tag></text_tag>`
  - Closing tag `<raw></raw>`
  - Closing tag `<link></link>`
  - Closing tag `<font></font>`, supports nesting other tags, such as `<font color=red>red<font color=green>green</font>again</font>`. Other tags include:
    - Closing tag `<local_datetime></local_datetime>`
    - Closing tag `<at></at>`
    - Closing tag `<a></a>`
    - Closing tag `<link></link>`
    - Closing tag `<font></font>`

Below are some common rendering effects and their corresponding Markdown or HTML syntax.

| Name | Syntax | Effect | Notes |
| --- | --- | --- | --- |
| Line Break | ```<br>Row 1<br>Row 2<br>Row 1<br />Row 2<br>``` | Row 1<br>Row 2 | - If you are building cards using Card JSON, you can also use the string newline syntax `\n` line breaks.<br>- If you are building cards with the Card Builder, you can also use the carriage return key to break lines. |
| Italic | ```<br>*Italic*<br>``` | _Italic_ | None |
| Bold | ```<br> __Bold__ <br>or<br> **Bold** <br>``` | **Bold** | - Do not use 4 consecutive `*` or `_` bolds. This syntax is not standardized and may result in incorrect rendering.<br>- If the bold effect is not displayed, ensure that there is a space before and after the bold syntax. |
| Strikethrough | ```<br>Strikethrough<br>``` | ~~Strikethrough~~ | None |
| Mention Specific Person | ```<br><at id=open_id></at><br><at id=user_id></at><br><at email=test@email.com></at><br><at ids=id_01,id_02,xxx></at><br>``` | @Username | - This syntax is used to achieve the effect of @ mentioning a person in the card, and the mentioned user will receive a mention notification. However, for forwarded cards, the user will no longer receive the mention notification.<br>  <br>- To display the username, avatar, and personal card of a person in the card, you can use the [User Profile](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/user-profile) or [User List](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/user-list) component. However, the person and person list components are for display only, and users will not receive mention notifications.<br>  <br>- [Custom robots](https://open.larksuite.com/document/ukTMukTMukTM/ucTM5YjL3ETO24yNxkjN) only support using `open_id`, `user_id` to mention specific people.<br>  <br>- You can use the `<at ids=id_01,id_02,xxx></at>` syntax to pass multiple IDs here. |
| Mention Everyone | ```<br><at id=all></at><br>``` | @everyone | Mentioning everyone requires group owner permission. If not enabled, the card will fail to send. |
| Hyperlink | ```<br><a href='https://open.larksuite.com'><br></a><br>``` | [https://open.larksuite.com](https://open.larksuite.com/) | - Hyperlinks must include a schema to be effective; currently, only HTTP and HTTPS are supported.<br>- The color of hyperlink text does not support customization. |
| Colored Text Style | ```<br><font color='green'><br>  This is green text<br></font><br><font color='red'><br>  This is red text<br></font><br><font color='grey'><br>  This is grey text<br></font><br>``` | ![](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/3cb544894ff14bd08697aba80d8e45e6~tplv-goo7wpa0wc-image.image?height=46&lazyload=true&width=206)![](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/20cf2f954cc34e79b1a9083ddf1c5838~tplv-goo7wpa0wc-image.image?height=46&lazyload=true&width=200)![](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/4c1721ac3ea6437fb52661d0f59d5b63~tplv-goo7wpa0wc-image.image?height=40&lazyload=true&width=192) | - Colored text styles do not apply to text in links<br>- Color values:<br>  - **default**: Default style with white background and black text<br>  - Supported color enumerations and RGBA syntax for custom colors. Refer to [Color Enumeration](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/enumerations-for-fields-related-to-color) |
| Clickable Phone Number | ```<br>[Display text for phone number or other content](tel://phone_number_to_popup_on_mobile)<br>``` | ![](https://sf16-sg.larksuitecdn.com/obj/open-platform-opendoc-sg/497e911ac70982442571a2671c7c178c_5i91YqPxhx.png?height=99&lazyload=true&width=789) | This syntax is effective only on mobile devices. |
| Text Link | ```<br>[Open Platform](https://open.larksuite.com/)<br>``` | [Open Platform](https://open.larksuite.com/) | Hyperlinks must include a schema to be effective; currently, only HTTP and HTTPS are supported. |
| Differential Redirection Link | ```<br>{<br> "tag": "markdown",<br> "href": {<br>  "urlVal": {<br>   "url": "xxx",<br>   "pc_url":"xxx",<br>   "ios_url": "xxx",<br>   "android_url": "xxx"<br>   }<br>  },<br> "content":<br> "[Differential Redirection]($urlVal)"<br>}<br>``` | - | - Hyperlinks must include a schema to be effective, currently only HTTP and HTTPS.<br>- Use only when different links are needed for PC and mobile platforms. |
| Image | ```<br>![hover_text](image_key)<br>``` | ![](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/be64df8f4f0c40b79140ba5c92e0b80b~tplv-goo7wpa0wc-image.image?height=582&lazyload=true&maxWidth=100&width=582) | - `hover_text` refers to the text displayed when the cursor hovers over the image on the PC.<br>- **image\_key** can be obtained by calling the [Upload Image](https://open.larksuite.com/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/image/create) API. |
| Divider | ```<br>---<br>``` | ![](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/337cdbabf3944d4facd505a9f9883352~tplv-goo7wpa0wc-image.image?height=62&lazyload=true&width=346) | The `---` symbol must be used on a separate line. That is, if there is text before and after the `---` symbol, you must add line breaks before and after the split line. |
| Lark Emoji | ```<br>:DONE:<br>``` | ![](https://sf3-ttcdn-tos.pstatp.com/obj/lark-reaction-cn/emoji_done.png?height=96&lazyload=true&width=96) | Supported Emoji Key list can be found in [Emoji Text Description](https://open.larksuite.com/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message-reaction/emojis-introduce). |
| Tag | ```<br><text_tag color='red'>Tag text</text_tag><br>``` | ![](https://sf16-sg.larksuitecdn.com/obj/open-platform-opendoc-sg/4105178f31cc40ef499feae123754098_W9hZbwm3fv.png?height=646&lazyload=true&maxWidth=68&width=188) | Supported `color` enumeration range includes:<br>- `neutral`: Neutral color<br>- `blue`: Blue<br>- `turquoise`: Turquoise<br>- `lime`: Lime<br>- `orange`: Orange<br>- `violet`: Violet<br>- `indigo`: Indigo<br>- `wathet`: Sky blue<br>- `green`: Green<br>- `yellow`: Yellow<br>- `red`: Red<br>- `purple`: Purple<br>- `carmine`: Carmine |
| Ordered List | ```<br>1. Ordered item 1<br>    1. Sub-item 1.1<br>2. Ordered item 2<br>``` | 1. Ordered item 1<br>   1. Sub-item 1.1<br>2. Ordered item 2 | - Numbers must be used at the start of the line<br>- 4 spaces represent one level of indentation<br>Only effective in Lark version 7.6 and above. In older versions of the Lark client, components containing this syntax will display an upgrade placeholder image. |
| Unordered List | ```<br>- Unordered item 1<br>    - Sub-item 1.1<br>- Unordered item 2<br>``` | - Unordered item 1<br>  - Sub-item 1.1<br>- Unordered item 2 | - Marks must be used at the start of the line<br>- 4 spaces represent one level of indentation<br>- In the card JSON, you need to add `\n` for line breaks:<br>  <br>  <br>  ```<br>  <br>  \n- Unordered list 1\n    - Unordered list 1.1\n- Unordered list 2\n1. Ordered list 1\n<br>  ```<br>  <br>Only effective in Lark version 7.6 and above. In older versions of the Lark client, components containing this syntax will display an upgrade placeholder image. |
| Code Block | ````<br>```JSON<br>{"This is": "JSON demo"}<br>```<br>```` | ```<br>{"This is": "JSON demo"}<br>``` | - Code block syntax and content must be used at the start of the line<br>- Supports specifying programming languages for parsing. If not specified, defaults to Plain Text<br>- Four or more spaces ( [indented code blocks](https://spec.commonmark.org/0.30/#indented-code-blocks)) will also trigger the code block effect. |
| Link with Icon | ```<br><link icon='chat_outlined' url='https://open.larksuite.com' pc_url='' ios_url='' android_url=''>Strategic Discussion</link><br>``` | ![](https://sf16-sg.larksuitecdn.com/obj/open-platform-opendoc-sg/e6b63f8c225ce6c4cd09dbdc8158397f_HPk70nRLtr.png?height=97&lazyload=true&width=736) | Field descriptions in this syntax are as follows:<br>- `icon`: Icon preceding the link. Only icons from the icon library are supported, see [Icon Library](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/enumerations-for-icons) for enumeration values. The icon color is fixed as blue. Optional.<br>- `url`: The default link address, effective when no device-specific fields are configured. Required.<br>- `pc_url`: PC link address, higher priority than `url`. Optional.<br>- `ios_url`: iOS link address, higher priority than `url`. Optional.<br>- `android_url`: Android link address, higher priority than `url`. Optional. |
| Personnel | ```<br>      <person id='user_id' show_name=true show_avatar=true style='normal'></person><br>``` | ![image.png](https://sf16-sg.larksuitecdn.com/obj/open-platform-opendoc-sg/85c9e79807d0195cd3ecb331a965f418_eFVjQrqRjv.png?height=95&lazyload=true&width=736) | The field descriptions for this syntax are as follows:<br>- `id`: The user's ID, which supports open\_id, union\_id, and user\_id. If left empty, incorrect, or omitted, it will display the fallback "Unknown User" style. For more information, refer to [How to Obtain Different User IDs](https://open.larksuite.com/document/home/user-identity-introduction/open-id).<br>- `show_name`: Whether to display the username. Defaults to true.<br>- `show_avatar`: Whether to display the user's avatar. Defaults to true.<br>- `style`: The display style of the personnel component. Available options are:<br>  - normal: Standard style (default)<br>  - capsule: Capsule style<br>Personnel syntax does not currently support previewing actual user avatars and names in the building tool. You can preview the actual effect by clicking **Send Me a Preview**. |
| Heading | ```<br># Heading Level 1<br>## Heading Level 2<br>###### Heading Level 6<br>``` | ![](https://sf16-sg.larksuitecdn.com/obj/open-platform-opendoc-sg/9f20da4d88e999dd95fb3afa7e7c178e_QzyatvgRcl.png?height=113&lazyload=true&width=725) | Supports heading levels from 1 to 6. The font sizes from level 1 to 6 are 26, 22, 20, 18, 17, and 14px.<br>Heading syntax can only be used in the [Card JSON 2.0 Structure](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-structure). |
| Blockquote | ```<br>>[Space] This is a blockquote text\nNew line in blockquote<br>``` | ![](https://sf16-sg.larksuitecdn.com/obj/open-platform-opendoc-sg/3551041c80d4879301b805e1c78d5c0d_OrdqP5rWoe.png?height=84&lazyload=true&width=209) | Blockquote syntax can only be used in the [Card JSON 2.0 Structure](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-structure). |
| Inline Code | ```<br>`code`<br>``` | ![](https://sf16-sg.larksuitecdn.com/obj/open-platform-opendoc-sg/b89bc8e45736ed3d48707591cb109383_TBPlo20031.png?height=48&lazyload=true&width=104) | Inline code syntax can only be used in the [Card JSON 2.0 Structure](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-structure). |
| Number Badge | ```<br><number_tag>1</number_tag><br>```<br>```<br><number_tag background_color='grey' font_color='white' url='https://open.larksuite.com' pc_url='https://open.larksuite.com' android_url='https://open.larksuite.com' ios_url='https://open.larksuite.com'>1</number_tag><br>``` | ![](https://sf16-sg.larksuitecdn.com/obj/open-platform-opendoc-sg/d97f3d4f1c0e73bb5fb7a267b1a4ecf7_tLSJTnxEsn.png?height=45&lazyload=true&width=141) | Circular number badges that support adding numbers from 0 to 99. The field descriptions for this syntax are as follows:<br>- `background_color`: Background color inside the circle. Optional.<br>- `font_color`: Font color of the number. Optional.<br>- `url`: Default link when clicking the badge. This configuration takes effect if the following device-specific fields are not configured. Optional.<br>- `pc_url`: Link when clicking the badge on the PC, with a higher priority than `url`. Optional.<br>- `ios_url`: Link when clicking the badge on iOS, with a higher priority than `url`. Optional.<br>- `android_url`: Link when clicking the badge on Android, with a higher priority than `url`. Optional.<br>Number badge syntax can only be used in the [Card JSON 2.0 Structure](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-structure). |
| Table | ```<br>| Syntax | Description |<br>| -------- | -------- |<br>| Paragraph | Text |<br>| Paragraph | Text |<br>| Paragraph | Text |<br>| Paragraph | Text |<br>| Paragraph | Text |<br>| Paragraph | Text |<br>``` | ![image.png](https://sf16-sg.larksuitecdn.com/obj/open-platform-opendoc-sg/8f518b1bfa0e2f217893c379d4c5e07a_6SH7H9f5ew.png?height=411&lazyload=true&maxWidth=200&width=882) | - Except for the header row, up to five rows of data is shown. Any data exceeding five rows will be paginated.<br>- A maximum of four tables can be placed in a single rich text component.<br>- The rich text syntax for tables does not support setting column width, etc. To set column width, data alignment, etc., you can use the [Table](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/table) component. |
| Internationalization time | `<local_datetime millisecond='' format_type='date_num' link='https://www.feishu.com'></local_datetime>` | ![image.png](https://sf16-sg.larksuitecdn.com/obj/open-platform-opendoc-sg/e3bf186ccbd69dcb9323284796ca39b8_624UOfinKt.png?height=358&lazyload=true&maxWidth=200&width=668) | Internationalization time tag. Supports automatic display of time in the user's local timezone. The fields in this syntax are described as follows:<br>- **`millisecond`**: The Unix millisecond timestamp of the time to be displayed. If not provided:<br>  <br>  - For cards sent using card JSON, the default is the time when the card was sent.<br>  - For cards built using the builder tool, the default is the time when the card was published.<br>- **`format_type`**: Defines the format of the time display. By default, it uses a numeric display, e.g., `2019-03-15`. The enumeration values are as follows:<br>  <br>  - `date_num`: Date represented by numbers, e.g., `2019-03-15`.<br>  - `date_short`: Abbreviated date without the year, supports automatic multilingual adaptation, e.g., `3月15日`, `Mar 15`.<br>  - `date`: Complete internationalized date text, supports automatic multilingual adaptation, e.g., `2019年3月15日`, `Mar 15, 2019`.<br>  - `week`: Complete week text, supports automatic multilingual adaptation, e.g., `星期二`, `Tuesday`.<br>  - `week_short`: Abbreviated week text, supports automatic multilingual adaptation, e.g., `周二`, `Tue`.<br>  - `time`: Time (hour:minute) text, e.g., `13:42`.<br>  - `time_sec`: Time (hour:minute:second) text, e.g., `13:42:53`.<br>  - `timezone`: Timezone of the device, formatted as `GMT±hh:mm`, e.g., `GMT+8:00`.<br>- **`link`**: The URL to redirect to when the time is clicked. |

### Explanation of special character escaping

If the characters you want to display hit the special characters used in markdown syntax (such as \*, ~, >, <), you need to HTML escape these special characters to display them normally. The escape character comparison table is as follows:

| **Special Character** | **Escape Sequence** | **Description** |
| --- | --- | --- |
| `` | `&nbsp;` | Non-break space |
| `` | `&ensp;` | Half-width space |
| `` | `&emsp;` | Full-width space |
| `>` | `&#62;` | Greater than symbol |
| `<` | `&#60;` | Less than symbol |
| `~` | `&sim;` | Tilde |
| `-` | `&#45;` | Hyphen |
| `!` | `&#33;` | Exclamation mark |
| `*` | `&#42;` | Asterisk |
| `/` | `&#47;` | Forward slash |
| `\` | `&#92;` | Backslash |
| `[` | `&#91;` | Left square bracket |\
| `]` | `&#93;` | Right square bracket |
| `(` | `&#40;` | Left parenthesis |
| `)` | `&#41;` | Right parenthesis |
| `#` | `&#35;` | Hash symbol |
| `:` | `&#58;` | Colon |
| `+` | `&#43;` | Plus sign |
| `"` | `&#34;` | Double quotation mark |
| `'` | `&#39;` | Single quotation mark |
| \` | `&#96;` | Backtick |
| `$` | `&#36;` | Dollar sign |
| `_` | `&#95;` | Underscore |
| `-` | `&#45;` | Unordered list mark |

For more escape characters, refer to the [HTML Escape Universal Standard](https://www.w3school.com.cn/charsets/ref_html_8859.asp) to implement them. The escaped format is `&#entity number;`.

### Programming languages supported by code blocks

The rich text component supports rendering code using code block syntax. The supported programming languages are listed below and are case-insensitive.

````

```JSON
{"This is": "JSON demo"}
```
````

- plain\_text
- abap
- ada
- apache
- apex
- assembly
- bash
- c\_sharp
- cpp
- c
- cmake
- cobol
- css
- coffee\_script
- d
- dart
- delphi
- diff
- django
- docker\_file
- erlang
- fortran
- gherkin
- go
- graphql
- groovy
- html
- htmlbars
- http
- haskell
- json
- java
- javascript
- julia
- kotlin
- latex
- lisp
- lua
- matlab
- makefile
- markdown
- nginx
- objective\_c
- opengl\_shading\_language
- php
- perl
- powershell
- prolog
- properties
- protobuf
- python
- r
- ruby
- rust
- sas
- scss
- sql
- scala
- scheme
- shell
- solidity
- swift
- toml
- thrift
- typescript
- vbscript
- visual\_basic
- xml
- yaml

## Defining Different Font Sizes for Mobile and Desktop

In the plain text and rich text components, you can define different font sizes for the same text on mobile and desktop platforms. The related field descriptions are as shown in the following table.

| Field | Required | Type | Default Value | Description |
| --- | --- | --- | --- | --- |
| text\_size | No | Object | / | Font size. You can customize different font sizes for mobile and desktop here. |
| └ custom\_text\_size\_name | No | Object | / | Custom font size. You need to define the name of this field, such as `cus-0`, `cus-1`, etc. |
| └└ default | No | String | / | The font size property that is effective on old versions of Lark clients that cannot differentiate configurations. Recommended to fill in this field. Available values are as follows.<br>- heading-0: Extra large title (30px)<br>- heading-1: First level title (24px)<br>- heading-2: Second level title (20 px)<br>- heading-3: Third level title (18px)<br>- heading-4: Fourth level title (16px)<br>- heading: Title (16px)<br>- normal: Text (14px)<br>- notation: Auxiliary information (12px)<br>- xxxx-large: 30px<br>- xxx-large: 24px<br>- xx-large: 20px<br>- x-large: 18px<br>- large: 16px<br>- medium: 14px<br>- small: 12px<br>- x-small: 10px |
| └└ pc | No | String | / | Desktop font size. Available values are as follows.<br>- heading-0: Extra large title (30px)<br>- heading-1: First level title (24px)<br>- heading-2: Second level title (20 px)<br>- heading-3: Third level title (18px)<br>- heading-4: Fourth level title (16px)<br>- heading: Title (16px)<br>- normal: Text (14px)<br>- notation: Auxiliary information (12px)<br>- xxxx-large: 30px<br>- xxx-large: 24px<br>- xx-large: 20px<br>- x-large: 18px<br>- large: 16px<br>- medium: 14px<br>- small: 12px<br>- x-small: 10px |
| └└ mobile | No | String | / | Mobile text font size. Available values are as follows.<br>**Note**: Some mobile font size enumeration values may differ from the PC version, so please use accordingly.<br>- heading-0: Extra large title (26px)<br>- heading-1: First level title (24px)<br>- heading-2: Second level title (20 px)<br>- heading-3: Third level title (17px)<br>- heading-4: Fourth level title (16px)<br>- heading: Title (16px)<br>- normal: Text (14px)<br>- notation: Auxiliary information (12px)<br>- xxxx-large: 26px<br>- xxx-large: 24px<br>- xx-large: 20px<br>- x-large: 18px<br>- large: 17px<br>- medium: 14px<br>- small: 12px<br>- x-small: 10px |

The specific steps are as follows.

1. In the global behavior settings of the card JSON code, configure the `style` field in the `config` section, and add custom font sizes:

```

{
     "config": {
       "style": { // Add and configure the style field here.
         "text_size": { // Add custom font sizes for mobile and desktop, also include a fallback font size. Used to set the font size property in the component JSON. Supports adding multiple custom font size objects.
           "cus-0": {
             "default": "medium", // The font size property that takes effect on old versions of Lark clients that cannot differentiate configurations. Optional.
             "pc": "medium", // Desktop font size.
             "mobile": "large" // Mobile font size.
           },
           "cus-1": {
             "default": "medium", // The font size property that takes effect on old versions of Lark clients that cannot differentiate configurations. Optional.
             "pc": "normal", // Desktop font size.
             "mobile": "x-large" // Mobile font size.
           }
         }
       }
     }
}
```

2. Apply the custom font size in the `text_size` property of the plain text or rich text component. Below is an example of applying a custom font size in a rich text component:

```

{
     "elements": [\
       {\
         "tag": "markdown",\
         "text_size": "cus-0", // Apply the custom font size here.\
         "href": {\
           "urlVal": {\
             "url": "xxx1",\
             "pc_url": "xxx2",\
             "ios_url": "xxx3",\
             "android_url": "xxx4"\
           }\
         },\
         "content": "Plain text\nStandard emoji😁😢🌞💼🏆❌✅\n*Italic*\n**Bold**\n~~Strikethrough~~\nText link\nDifferentiated redirection\n<at id=all></at>"\
       },\
       {\
         "tag": "hr"\
       },\
       {\
         "tag": "markdown",\
         "content": "The line above is a divider\n!hover_text\nThe line above is an image tag"\
       }\
     ],
     "header": {
       "template": "blue",
       "title": {
         "content": "This is the card title bar",
         "tag": "plain_text"
       }
     }
}
```


Feedback

[Previous:Plain text](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/plain-text) [Next:Image](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/image)

Need help with a problem?

Submit feedback

Please log in first before exploring any API.

Log In

RUN [Go to API Explorer](https://open.larksuite.com/api-explorer?from=op_doc&)

Need help with a problem?

Submit feedback

The contents of this article

[Notes](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/rich-text#0ff01b6a "Notes")

[Component properties](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/rich-text#1e2dc47b "Component properties")

[JSON structure](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/rich-text#3282a63a "JSON structure")

[Field descriptions](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/rich-text#622dac8e "Field descriptions")

[Demo example](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/rich-text#3f705c44 "Demo example")

[Supported Markdown syntax](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/rich-text#3dcaec43 "Supported Markdown syntax")

[Explanation of special character escaping](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/rich-text#6fb8622f "Explanation of special character escaping")

[Programming languages supported by code blocks](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/rich-text#7258688d "Programming languages supported by code blocks")

[Defining Different Font Sizes for Mobile and Desktop](https://open.larksuite.com/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-json-v2-components/content-components/rich-text#884a5e5d "Defining Different Font Sizes for Mobile and Desktop")

Try It

Feedback

OnCall

Collapse

Expand

We use cookies and similar technologies to provide and maintain our services and ensure performance, security, and stability of our website. We also use first and third party cookies for analytics and marketing purposes. Learn more about how we use cookies in our [Cookie Policy](https://www.larksuite.com/en_us/cookie-policy). You can manage your cookie preference at any time.

Got ItManage Settings