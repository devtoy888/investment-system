- [Home](https://open.feishu.cn/document/home/index)
- [Developer Guides](https://open.feishu.cn/document/client-docs/intro)
- [Developer Tutorials](https://open.feishu.cn/document/course)
- [Server API](https://open.feishu.cn/document/ukTMukTMukTM/ukDNz4SO0MjL5QzM/AI-assistant-code-generation-guide)
- [Client API](https://open.feishu.cn/document/client-docs/h5/)
- [Lark CLI](https://open.feishu.cn/document/mcp_open_tools/overview-of-lark-agent-integration-capabilities)
- [Feishu Plugin for OpenClaw](https://bytedance.larkoffice.com/docx/MFK7dDFLFoVlOGxWCv5cTXKmnMh)

API Explorer [CardKit](https://open.feishu.cn/cardkit?from=open_docs_header)

Search content

Platform Introduction

Develop Process

Develop Bots

Develop Web Apps

Develop Gadgets (Not Recommended)

Develop Docs Add-ons

Develop Base Extensions

Develop Workplace Blocks

Development link preview

Feishu Cards

[Feishu Card overview](https://open.feishu.cn/document/feishu-cards/feishu-card-overview)

Quick Start

Build card with Cardkit

Build card with JSON

[Card JSON v2.0 breaking changes & release notes](https://open.feishu.cn/document/feishu-cards/card-json-v2-breaking-changes-release-notes)

[Card JSON 2.0 structure](https://open.feishu.cn/document/feishu-cards/card-json-v2-structure)

Card JSON 2.0 version components

[Card JSON 1.0 structure](https://open.feishu.cn/document/feishu-cards/card-json-structure)

Card JSON 1.0 version components

[Component overview](https://open.feishu.cn/document/feishu-cards/card-components/component-overview)

Containers

Display components

[Title](https://open.feishu.cn/document/feishu-cards/card-components/content-components/title)

[Plain text](https://open.feishu.cn/document/feishu-cards/card-components/content-components/plain-text)

[Rich text](https://open.feishu.cn/document/feishu-cards/card-components/content-components/rich-text)

[Image](https://open.feishu.cn/document/feishu-cards/card-components/content-components/image)

[Multi-image laylout](https://open.feishu.cn/document/feishu-cards/card-components/content-components/multi-image-laylout)

[Divider](https://open.feishu.cn/document/feishu-cards/card-components/content-components/divider)

[User profile](https://open.feishu.cn/document/feishu-cards/card-components/content-components/user-profile)

[User list](https://open.feishu.cn/document/feishu-cards/card-components/content-components/user-list)

[Chart](https://open.feishu.cn/document/feishu-cards/card-components/content-components/chart)

[Table](https://open.feishu.cn/document/feishu-cards/card-components/content-components/table)

[Note](https://open.feishu.cn/document/feishu-cards/card-components/content-components/note)

Interactive components

[Configuring card interactions](https://open.feishu.cn/document/feishu-cards/configuring-card-interactions)

[Configure multi-language content](https://open.feishu.cn/document/feishu-cards/configure-multi-language-content)

[Send Feishu card](https://open.feishu.cn/document/feishu-cards/send-feishu-card)

[Handle card callbacks](https://open.feishu.cn/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/handle-card-callbacks)

[Update Feishu card](https://open.feishu.cn/document/feishu-cards/update-feishu-card)

[Feishu Card FAQs](https://open.feishu.cn/document/common-capabilities/message-card/message-card)

Resources

Web Components

Native integration

SSO&End User Consent

AppLink Protocol

Developer Tools

FAQ

Management Practice

Platform Notices

Deprecated Guides

[Developer Guides](https://open.feishu.cn/document/client-docs/intro) [Feishu Cards](https://open.feishu.cn/document/feishu-cards/feishu-card-overview) [Build card with JSON](https://open.feishu.cn/document/feishu-cards/card-json-v2-breaking-changes-release-notes) [Card JSON 1.0 version components](https://open.feishu.cn/document/feishu-cards/card-components/component-overview) [Display components](https://open.feishu.cn/document/feishu-cards/card-components/content-components/title)

Table

# Table

Copy Page

Last updated on 2025-01-02

The contents of this article

[Precautions](https://open.feishu.cn/document/feishu-cards/card-components/content-components/table#d258cc64 "Precautions")

[Nesting Rules](https://open.feishu.cn/document/feishu-cards/card-components/content-components/table#2d03520e "Nesting Rules")

[Component Properties](https://open.feishu.cn/document/feishu-cards/card-components/content-components/table#10a18a65 "Component Properties")

[JSON Structure](https://open.feishu.cn/document/feishu-cards/card-components/content-components/table#57118eda "JSON Structure")

[Field Descriptions](https://open.feishu.cn/document/feishu-cards/card-components/content-components/table#62f31792 "Field Descriptions")

[Sample code](https://open.feishu.cn/document/feishu-cards/card-components/content-components/table#8493ad2c "Sample code")

# Table component

Feishu cards support table components and allow the addition of plain text, markdown, option tags, personnel lists, date, and numeric content within the tables.

## Precautions

- The table component supports Feishu V7.4 and above versions of the client. On Feishu clients below this version, the content of the table will be displayed as a placeholder image saying "Please upgrade the client to the latest version to view the content."
- Each card can accommodate up to five table components. If the card is configured for multiple languages, each language can accommodate up to five table components.
- When there is insufficient space to display the full content within a cell, the content will be truncated at the end. On the client side, users can view the truncated content by hovering their cursor over the cell or by clicking on it.

## Nesting Rules

- The table component cannot be embedded within other components and can only be placed under the card's root node.
- The table component does not support embedding other components.

## Component Properties

### JSON Structure

The complete JSON data for the table component is as follows:

```

{ // Supported from 7.4
  "tag": "table", // The label of the component. The fixed value for the table component is table.
  "page_size": 5, // Maximum number of data rows displayed per page. Supports integers [1,10]. Default value is 5.
  "row_height": "low", // Row height setting. Default value is low.
  "freeze_first_column": true, // Whether to freeze the first column, default is false.
  "header_style": {
    // Set the header here.
    "text_align": "left", // Text alignment method. Default value is left.
    "text_size": "normal", // Text size. Default value is normal.
    "background_style": "none", // Background color. Default value is none.
    "text_color": "grey", // Text color. Default value is default.
    "bold": true, // Whether to bold. Default value is true.
    "lines": 1 // Number of text lines. Default value is 1.
  },
  "columns": [ // Add columns here. Supports up to 50 columns, content beyond 50 columns will not be displayed.\
    { // Add columns whose data type is plain text without formatting.\
      "name": "customer_name", // Custom column marker. Required. Used to uniquely specify which cell in the array of row data objects the data should be filled into.\
      "display_name": "Customer Name", // Column name. If empty, the column name is not displayed.\
      "width": "auto", // Column width. Default value is auto.\
      "data_type": "text", // Data type of the column.\
      "vertical_align": "top", // The vertical alignment of data within the column. Default value is center.\
      "horizontal_align": "left" // Data alignment within the column. Default value is left.\
    },\
    { // Add columns with lark_md text data type.\
      "name": "customer_link",\
      "display_name": "related_links",\
      "data_type": "lark_md"\
    },\
    { // Add a column of type number.\
      "name": "customer_arr",\
      "display_name": "ARR (ten thousand yuan)",\
      "data_type": "number",\
      "format": { // Configuration field when the column data type is number\
        "symbol": "¥", // Currency unit displayed before the number. Supports a single character of currency unit text. Optional.\
        "precision": 2, // Number of decimal places. Supports integers [0,10]. Default is unlimited decimal places.\
        "separator": true // Whether to enable comma-separated thousands format. Default value is false.\
      },\
      "width": "120px"\
    },\
    { // Add columns of type option.\
      "name": "customer_scale",\
      "display_name": "customer_scale",\
      "data_type": "options"\
    },\
    { // Add the column with type personnel.\
      "name": "customer_scale",\
      "display_name": "customer_docking_person",\
      "data_type": "persons"\
    },\
    { // Add a column of type date.\
      "name": "meeting_date",\
      "display_name": "docking_times",\
      "data_type": "date",\
      "date_format": "YYYY/MM/DD"\
    },\
    { // Add columns of type markdown text.\
      "name": "company_image",\
      "display_name": "company_image",\
      "data_type": "markdown"\
    }\
  ],
  "rows": [\
    // Add row data here.  Data value corresponding to the column definition. Defined as "name":VALUE, specifying the content of each row's data. name is your custom column marker.\
    {\
      "customer_name": "飞书科技",\
      "customer_date": 1699341315000,\
      "customer_scale": [\
        {\
          "text": "S2",\
          "color": "blue"\
        }\
      ],\
      "customer_arr": 168,\
      "customer_poc": [\
        "ou_14a32f1a02e64944cf19207aa43abcef",\
        "ou_e393cf9c22e6e617a4332210d2aabcef"\
      ],\
      "customer_link": "[飞书科技](/ssl:ttdoc/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message-reaction/emojis-introduce)"\
    },\
    {\
      "customer_name": "飞书科技_01",\
      "customer_date": 1606101072000,\
      "customer_scale": [\
        {\
          "text": "S1",\
          "color": "red"\
        }\
      ],\
      "customer_arr": 168.23,\
      "customer_poc": "ou_14a32f1a02e64944cf19207aa43abcef",\
      "customer_link": "[飞书科技_01](/ssl:ttdoc/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message-reaction/emojis-introduce)",\
      "company_image": "![image.png](image_key)"\
    },\
    {\
      "customer_name": "飞书科技_02",\
      "customer_date": 1606101072000,\
      "customer_scale": [\
        {\
          "text": "S3",\
          "color": "orange"\
        }\
      ],\
      "customer_arr": 168.23,\
      "customer_poc": "ou_14a32f1a02e64944cf19207aa43abcef",\
      "customer_link": "[飞书科技_02](/ssl:ttdoc/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message-reaction/emojis-introduce)",\
      "company_image": "![image.png](image_key)"\
    },\
    {\
      "customer_name": "飞书科技_03",\
      "customer_date": 1606101072000,\
      "customer_scale": [\
        {\
          "text": "S2",\
          "color": "blue"\
        }\
      ],\
      "customer_arr": 168.23,\
      "customer_poc": "ou_14a32f1a02e64944cf19207aa43abcef",\
      "customer_link": "[飞书科技_03](/ssl:ttdoc/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message-reaction/emojis-introduce)",\
      "company_image": "![image.png](image_key)"\
    }\
  ]
}
```

## Field Descriptions

The field descriptions for the table component are as follows.

| Field | Required | Type | Default Value | Description |
| --- | --- | --- | --- | --- |
| tag | Yes | String | / | The label of the component. The fixed value for the table component is table. |
| page\_size | No | Number | 5 | Maximum number of data rows displayed per page. Supports integers \[1,10\]. |
| row\_height | No | String | low | Row height of the table. If the cell height does not display the entire content of a row, the content is clipped top and bottom. Possible values:<br>- low: Low<br>- middle: Medium<br>- high: High<br>- \[32,124\]px: Custom row height, in pixels, such as 40px. The range is \[32,124\]. |
| header\_style | No | header\_style | / | Header style setting. See below for header\_style field descriptions. |
| freeze\_first\_column | No | Boolean | false | Whether to freeze the first column. Possible values are:<br>- true: Freezes the first column. When scrolling the table horizontally, the first column remains fixed, and other columns stack beneath it.<br>- false: Does not freeze the first column. When scrolling the table horizontally, all columns scroll together. |
| columns | Yes | column\[\] | \[\] | Array of column objects. See below for column field descriptions. |
| rows | Yes | JSON | \[\] | Array of row objects. Data corresponding to the column definitions. Defined as "name":VALUE, specifying the content of each row's data. name is your custom column marker. |

#### `header_style` Field Explanation

`header_style` is used to set the style and design of the table header. The subfields of `header_style` are shown in the following table.

| Field | Required | Type | Default Value | Description |
| --- | --- | --- | --- | --- |
| text\_align | No | String | left | Text alignment of the table header. Possible values:<br>- left: Left-aligned<br>- center: Center-aligned<br>- right: Right-aligned |
| text\_size | No | String | normal | Text size of the table header. Possible values:<br>- normal: Body text (14px)<br>- heading: Heading (16px) |
| background\_style | No | String | none | Background color of the table header. Possible values:<br>- grey: Gray<br>- none: No background color |
| text\_color | No | String | default | Text color. Possible values:<br>- default: Black in client light mode, white in dark mode<br>- grey: Gray |
| bold | No | Boolean | true | Whether the table header text is bold. Possible values:<br>- true: Bold<br>- false: Not bold |
| lines | No | Number | 1 | Number of lines for the table header text. Supports integers greater than or equal to 1. |

#### **`column`** Field Explanation

`column` is used to define the columns of the table. A maximum of 50 columns can be added; content beyond 50 columns will not be displayed.

| Field | Required | Type | Default Value | Description |
| --- | --- | --- | --- | --- |
| name | Yes | String | Empty | Custom column identifier. Used to uniquely specify in the row data object array, which cell the data should be filled into. |
| display\_name | No | String | Empty | Column name displayed in the header. If not filled or empty, the column name will not be displayed. |
| width | No | String | auto | Column width. Possible values:<br>- auto: Auto-adjusts to content width<br>- Custom width: Sets the column width in pixels, such as 120px. Value range is \[80px,600px\] integers<br>- Custom width percentage: Sets the column width as a percentage of the current table canvas width (table canvas width = card width - card left/right padding), such as 25%. Value range is \[1%,100%\] |
| vertical\_align | No | String | center | The vertical alignment of data within the column. Possible values:<br>- top: Top-aligned<br>- center: Center-aligned<br>- bottom: Bottom-aligned |
| horizontal\_align | No | String | left | Data alignment within the column. Possible values:<br>- left: Left-aligned<br>- center: Center-aligned<br>- right: Right-aligned |
| data\_type | Yes | String | text | Column data type. Possible values:Column Data Types. The optional values are as follows. For information on how to use different types, refer to the `data_type` field description section.<br>- **text**: Plain text without formatting. This is the default value for `data_type`.<br>- **lark\_md**: Text supporting partial Markdown format. Supported from Feishu v7.10 onwards. For details, refer to [Plain Text - Markdown Syntax Supported by lark\_md](https://open.feishu.cn/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-components/content-components/plain-text).<br>- **options**: Option tags. The text content within the tag should not be too long to avoid incomplete display on both PC and mobile devices. For longer text, consider using the text or lark\_md type.<br>- **number**: Numbers. By default, displayed right-aligned in the cell. If you select this data type, you can continue to add the `format` field in the `column` to set the number format attributes.<br>- **persons**: List of people. Displayed as user name + avatar.<br>- **date**: Date and time. Requires input in Unix standard millisecond timestamp. The Feishu client will display the date and time according to the user's local time zone. Supported from Feishu v7.6 onwards.<br>- **markdown**: Text supporting full Markdown syntax. For details, refer to [Rich Text (Markdown) Component](https://open.feishu.cn/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-components/content-components/rich-text). Supported from Feishu v7.14 onwards. |
| format | No | Object | / | This field is only effective when `data_type` is `number`. Here, you can choose to set decimal places, currency units, and thousands separator styles. |
| └ precision | No | Int | Empty | Decimal places of the number. By default, the number of decimal places is not limited, and the developer's input is displayed as is. You can fill in an integer from 0 to 10. A decimal place of 0 means rounding to an integer. |
| └ symbol | No | String | Empty | Currency unit before the number. If not filled or empty, it is not displayed. You can fill in a one-character currency unit text, such as "¥". |
| └ separator | No | Boolean | false | Whether to apply the thousands separator comma style to the number. |
| date\_format | 否 | String | 空 | This field is only effective when `data_type` is `date`. You can select the following date-time placeholders as needed and combine them with any delimiters.<br>- YYYY: Year<br>- MM: Month<br>- DD: Day<br>- HH: Hour<br>- mm: Minute<br>- ss: Second<br>The following date formats are recommended. By default, the date and time are displayed according to the RFC 3339 standard format.<br>- YYYY/MM/DD<br>- YYYY/MM/DD HH:mm<br>- YYYY-MM-DD<br>- YYYY-MM-DD HH:mm<br>- DD/MM/YYYY<br>- MM/DD/YYYY |

#### `data_type` Field Description

The `data_type` field is used to specify the data type of a column. The supported enumeration values for `data_type` and their detailed descriptions are as follows.

| data\_type Enum | Supported Version | Description | Data Structure and Example |
| --- | --- | --- | --- |
| text | Feishu v7.4 and above | Plain text without formatting. This is the default value for `data_type`. | Structure:<br>```<br>"name": "plain text"  // If not filled or empty, it will display an empty cell. Non-string types will be converted to string for display.<br>```<br>Example:<br>```<br>"business_domain_name": "Feishu Card"<br>``` |
| lark\_md | Feishu v7.10 and above | Text supporting partial Markdown format. For details, refer to [Plain Text - Markdown Syntax Supported by lark\_md](https://open.feishu.cn/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-components/content-components/plain-text). | Structure:<br>```<br>"name": "[Text Link](https://www.feishu.cn)"  // If not filled or empty, it will display an empty cell. Non-string types will be converted to string for display.<br>```<br>Example:<br>```<br>"customer_link": "[Feishu Technology_01](/ssl:ttdoc/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message-reaction/emojis-introduce)"<br>``` |
| options | Feishu v7.4 and above | Option tags. Supports customizing the tag color using the `color` parameter. The color enumeration values and display effects are as follows. The default value is blue.<br>**Note**:The text content within the tag should not be too long to avoid incomplete display on both PC and mobile devices. For longer text, consider using the text or lark\_md type.<br>![](https://sf3-cn.feishucdn.com/obj/open-platform-opendoc/7dce9769aa1475bb36bada6533775403_nCnDT2EAmq.png?height=494&lazyload=true&width=1722) | Structure:<br>```<br>// Supports displaying a single default style tag<br>"name": "option"<br>// Supports displaying multiple custom style tags<br>"name": [<br>{<br>"text": "option 1",<br>"color": "red"<br>},<br>{<br>"text": "option 2",<br>"color": "green"<br>}<br>]<br>```<br>Example:<br>```<br>"customer_scale": [<br>{<br>"text": "S2",<br>"color": "green"<br>}<br>]<br>``` |
| number | Feishu v7.4 and above | Numbers. By default, displayed right-aligned in the cell. Supports adding a `format` field to set the number format attributes. For details, refer to the `format` field description. | Structure:<br>```<br>"name": NUMBER<br>```<br>Example:<br>```<br>"customer_arr": 26.57774928467545<br>``` |
| persons | Feishu v7.4 and above | List of people. Displayed as user name + avatar. Supports specifying people by user ID, which can be `user_id`, `open_id`, `union_id`, or `lark_id`. For more information about IDs, refer to [User Identity Overview](https://open.feishu.cn/document/home/user-identity-introduction/introduction).<br>**Note**: If the user ID is invalid, it will display as "Unknown User". | Structure:<br>```<br>"name": [<br>"user_id_1",<br>"user_id_2",<br>…<br>] // Display multiple people<br>or<br>"name": "user_id" // Display a single person<br>```<br>Example:<br>```<br>"customer_name": "ou_c99c5f35d542efc7ee492afe11af19ef"<br>``` |
| date | Feishu v7.6 and above | Date and time. Requires input in Unix standard millisecond timestamp. The Feishu client will display the date and time according to the user's local time zone.<br>Supports adding a `date_format` field to set the date format attributes. By default, it displays the date and time in RFC 3339 standard format. For details, refer to the `date_format` field description. | Structure:<br>```<br>"name": NUMBER<br>```<br>Example:<br>```<br>"customer_date": 1606101072000  // Millisecond timestamp<br>``` |
| markdown | Feishu v7.14 and above | Text supporting full Markdown syntax. For details, refer to the [Rich Text (Markdown)](https://open.feishu.cn/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/card-components/content-components/rich-text) component. | Structure:<br>```<br>"name": "markdown text"  // If not filled or empty, it will display an empty cell. Non-string types will be converted to string for display.<br>```<br>Example:<br>```<br>"company_image": "![image.png](img_v3_02cc_bf88cdee-6650-4b39-987c-f8e87c3227fg)"<br>``` |

## Sample code

The following JSON sample code can achieve the card effect as shown in the image below.

![](https://sf3-cn.feishucdn.com/obj/open-platform-opendoc/0b621b9ae52f1106965dcfb022ffcb4b_EI5Extg7gI.gif?height=392&lazyload=true&maxWidth=434&width=772)

```

{
  "header": {
    "template": "blue",
    "title": {
      "content": "表格组件（依赖端版本 7.4+)",
      "tag": "plain_text"
    }
  },
  "elements": [\
    {\
      "tag": "table",\
      "page_size": 5,\
      "row_height": "low",\
      "header_style": {\
        "text_align": "left",\
        "text_size": "normal",\
        "background_style": "none",\
        "text_color": "grey",\
        "bold": true,\
        "lines": 1\
      },\
      "columns": [\
        {\
          "name": "customer_name",\
          "display_name": "客户名称",\
          "data_type": "text",\
          "horizontal_align": "left",\
          "vertical_align": "top",\
          "width": "auto"\
        },\
        {\
          "name": "customer_scale",\
          "display_name": "客户规模",\
          "data_type": "options",\
          "horizontal_align": "left",\
          "vertical_align": "top",\
          "width": "auto"\
        },\
        {\
          "name": "customer_arr",\
          "display_name": "ARR(万元)",\
          "data_type": "number",\
          "format": {\
            "symbol": "¥",\
            "precision": 2,\
            "separator": true\
          },\
          "width": "auto"\
        },\
        {\
          "name": "customer_poc",\
          "display_name": "跟进人",\
          "data_type": "persons",\
          "horizontal_align": "left",\
          "vertical_align": "top",\
          "width": "auto"\
        },\
        {\
          "name": "customer_date",\
          "display_name": "签约日期",\
          "data_type": "date",\
          "date_format": "YYYY/MM/DD",\
          "width": "auto"\
        },\
        {\
          "name": "customer_link",\
          "display_name": "相关链接",\
          "data_type": "lark_md",\
          "width": "auto"\
        },\
        {\
            "name": "company_image",\
            "display_name": "企业图片",\
            "data_type": "markdown"\
        }\
      ],\
      "rows": [\
        {\
          "customer_name": "飞书科技",\
          "customer_date": 1699341315000,\
          "customer_scale": [\
            {\
              "text": "S2",\
              "color": "blue"\
            }\
          ],\
          "customer_arr": 168,\
          "customer_poc": [\
            "ou_14a32f1a02e64944cf19207aa43abcef",\
            "ou_e393cf9c22e6e617a4332210d2aabcef"\
          ],\
          "customer_link": "[飞书科技](/document-mod/index?fullPath=/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message-reaction/emojis-introduce)",\
          "company_image": "![image.png](img_v3_02cc_bf88cdee-6650-4b39-987c-f8e87c3227fg)"\
        },\
        {\
          "customer_name": "飞书科技_01",\
          "customer_date": 1606101072000,\
          "customer_scale": [\
            {\
              "text": "S1",\
              "color": "red"\
            }\
          ],\
          "customer_arr": 168.23,\
          "customer_poc": "ou_14a32f1a02e64944cf19207aa43abcef",\
          "customer_link": "[飞书科技_01](/document-mod/index?fullPath=/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message-reaction/emojis-introduce)",\
          "company_image": "![image.png](img_v3_02cc_bf88cdee-6650-4b39-987c-f8e87c3227fg)"\
        },\
        {\
          "customer_name": "飞书科技_02",\
          "customer_date": 1606101072000,\
          "customer_scale": [\
            {\
              "text": "S3",\
              "color": "orange"\
            }\
          ],\
          "customer_arr": 168.23,\
          "customer_poc": "ou_14a32f1a02e64944cf19207aa43abcef",\
          "customer_link": "[飞书科技_02](/document-mod/index?fullPath=/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message-reaction/emojis-introduce)",\
          "company_image": "![image.png](img_v3_02cc_bf88cdee-6650-4b39-987c-f8e87c3227fg)"\
        },\
        {\
          "customer_name": "飞书科技_03",\
          "customer_date": 1606101072000,\
          "customer_scale": [\
            {\
              "text": "S2",\
              "color": "blue"\
            }\
          ],\
          "customer_arr": 168.23,\
          "customer_poc": "ou_14a32f1a02e64944cf19207aa43abcef",\
          "customer_link": "[飞书科技_03](/document-mod/index?fullPath=/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message-reaction/emojis-introduce)",\
          "company_image": "![image.png](img_v3_02cc_bf88cdee-6650-4b39-987c-f8e87c3227fg)"\
        }\
      ]\
    }\
  ]
}
```

[Explain](https://open.feishu.cn/app/ai/playground?query=Based%20on%20the%20doc%20at%20https%3A%2F%2Fopen.feishu.cn%2Fdocument%2Ffeishu-cards%2Fcard-components%2Fcontent-components%2Ftable%2C%20explain%20what%20%22%22%20means&from=doc_text_select) Document Error Correction

Need help? Try asking AI Assistant

[Previous:Chart](https://open.feishu.cn/document/feishu-cards/card-components/content-components/chart) [Next:Note](https://open.feishu.cn/document/feishu-cards/card-components/content-components/note)

Please log in first before exploring any API.

Log In

RUN [Go to API Explorer](https://open.feishu.cn/api-explorer?from=op_doc&)

The contents of this article

[Precautions](https://open.feishu.cn/document/feishu-cards/card-components/content-components/table#d258cc64 "Precautions")

[Nesting Rules](https://open.feishu.cn/document/feishu-cards/card-components/content-components/table#2d03520e "Nesting Rules")

[Component Properties](https://open.feishu.cn/document/feishu-cards/card-components/content-components/table#10a18a65 "Component Properties")

[JSON Structure](https://open.feishu.cn/document/feishu-cards/card-components/content-components/table#57118eda "JSON Structure")

[Field Descriptions](https://open.feishu.cn/document/feishu-cards/card-components/content-components/table#62f31792 "Field Descriptions")

[Sample code](https://open.feishu.cn/document/feishu-cards/card-components/content-components/table#8493ad2c "Sample code")

Try It

Feedback

OnCall

Collapse

Expand