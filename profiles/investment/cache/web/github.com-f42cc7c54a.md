[Skip to content](https://github.com/simonlin1212/Vibe-Research/blob/main/frontend/src/pages/Portfolio.tsx#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/simonlin1212/Vibe-Research/blob/main/frontend/src/pages/Portfolio.tsx) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/simonlin1212/Vibe-Research/blob/main/frontend/src/pages/Portfolio.tsx) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/simonlin1212/Vibe-Research/blob/main/frontend/src/pages/Portfolio.tsx) to refresh your session.Dismiss alert

{{ message }}

[simonlin1212](https://github.com/simonlin1212)/ **[Vibe-Research](https://github.com/simonlin1212/Vibe-Research)** Public

- [Notifications](https://github.com/login?return_to=%2Fsimonlin1212%2FVibe-Research) You must be signed in to change notification settings
- [Fork\\
208](https://github.com/login?return_to=%2Fsimonlin1212%2FVibe-Research)
- [Star\\
931](https://github.com/login?return_to=%2Fsimonlin1212%2FVibe-Research)


## Collapse file tree

## Files

main

Search this repository(forward slash)` forward slash/`

/

# Portfolio.tsx

Copy path

Blame

More file actions

Blame

More file actions

## Latest commit

[![simonlin1212](https://avatars.githubusercontent.com/u/166034225?v=4&size=40)](https://github.com/simonlin1212)[simonlin1212](https://github.com/simonlin1212/Vibe-Research/commits?author=simonlin1212)

[fix: ETF 行情、持仓成本精度、用户数据防丢迁移 (](https://github.com/simonlin1212/Vibe-Research/commit/155e2eb0b0a516a948e33babfb772afe3da6fa8c) [#10](https://github.com/simonlin1212/Vibe-Research/issues/10) [#12](https://github.com/simonlin1212/Vibe-Research/issues/12) [#13](https://github.com/simonlin1212/Vibe-Research/issues/13) [)](https://github.com/simonlin1212/Vibe-Research/commit/155e2eb0b0a516a948e33babfb772afe3da6fa8c)

Open commit details

2 weeks agoJul 10, 2026

[155e2eb](https://github.com/simonlin1212/Vibe-Research/commit/155e2eb0b0a516a948e33babfb772afe3da6fa8c) · 2 weeks agoJul 10, 2026

## History

[History](https://github.com/simonlin1212/Vibe-Research/commits/main/frontend/src/pages/Portfolio.tsx)

Open commit details

[View commit history for this file.](https://github.com/simonlin1212/Vibe-Research/commits/main/frontend/src/pages/Portfolio.tsx) History

304 lines (285 loc) · 15.7 KB

/

# Portfolio.tsx

Copy path

Top

## File metadata and controls

- Code

- Blame


304 lines (285 loc) · 15.7 KB

[Raw](https://github.com/simonlin1212/Vibe-Research/raw/refs/heads/main/frontend/src/pages/Portfolio.tsx)

Copy raw file

Download raw file

You must be signed in to make or propose changes

More edit options

Open symbols panel

Edit and raw actions

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

40

41

42

43

44

45

46

47

48

49

50

51

52

53

54

55

56

57

58

59

60

61

62

63

64

65

66

67

68

69

70

71

72

73

74

75

76

77

78

79

80

81

82

83

84

85

86

87

88

89

90

91

92

93

94

95

96

97

98

99

100

101

102

103

104

105

106

107

108

109

110

111

112

113

114

115

116

117

118

119

120

121

122

123

124

125

126

127

128

129

130

131

132

133

134

135

136

137

138

139

140

141

142

143

144

145

146

147

148

149

150

151

152

153

154

155

156

157

158

159

160

161

162

163

164

165

166

167

168

169

170

171

172

173

174

175

176

177

178

179

180

181

182

183

184

185

186

187

188

189

190

191

192

193

194

195

196

197

198

199

200

201

202

203

204

205

206

207

208

209

210

211

212

213

214

215

216

217

218

219

220

221

222

223

224

225

226

227

228

229

230

231

232

233

234

235

236

237

238

239

240

241

242

243

244

245

246

247

248

249

250

251

252

253

254

255

256

257

258

259

260

261

262

263

264

265

266

267

268

269

270

271

272

273

274

275

276

277

278

279

280

281

282

283

284

285

286

287

288

289

290

291

292

293

294

295

296

297

298

299

300

301

302

303

304

import{useState,useEffect,useCallback}from"react";

import{Plus,ShieldCheck,RefreshCw,Loader2,Trash2,AlertCircle}from"lucide-react";

import{PageHeader}from"@/components/ui/PageHeader";

import{GlassCard}from"@/components/ui/GlassCard";

import{AskAiButton}from"@/components/ui/AskAiButton";

import{Disclaimer}from"@/components/ui/Disclaimer";

import{api,ApiError,typePortfolioData}from"@/lib/api";

import{cn}from"@/lib/utils";

constREFRESH\_MS=30\*60\*1000;// 每半小时自动刷新

constpnlColor=(v: number)=>(v>0 ? "text-danger" : v<0 ? "text-success" : "text-muted-foreground");

constfmt=(v: number)=>v.toLocaleString("zh-CN",{maximumFractionDigits: 2});

// 单价类（现价/成本/清仓价）最多 4 位小数：ETF/基金常见 3-4 位，截断成 2 位会与市值/盈亏对不上账

constfmtPx=(v: number)=>v.toLocaleString("zh-CN",{maximumFractionDigits: 4});

exportfunctionPortfolio(){

const\[data,setData\]=useState<PortfolioData\|null>(null);

const\[err,setErr\]=useState<string\|null>(null);

const\[refreshing,setRefreshing\]=useState(false);

const\[code,setCode\]=useState("");

const\[shares,setShares\]=useState("");

const\[cost,setCost\]=useState("");

const\[adding,setAdding\]=useState(false);

// 清仓录入

const\[cCode,setCCode\]=useState("");

const\[cDate,setCDate\]=useState("");

const\[cPrice,setCPrice\]=useState("");

const\[cShares,setCShares\]=useState("");

const\[cCost,setCCost\]=useState("");

const\[closing,setClosing\]=useState(false);

constload=useCallback(async(manual=false)=>{

if(manual)setRefreshing(true);

try{

setData(manual ? awaitapi.refreshPortfolio() : awaitapi.portfolio());

setErr(null);

}catch(e){

setErr(einstanceofApiError ? e.message : "加载失败");

}finally{

if(manual)setRefreshing(false);

}

},\[\]);

useEffect(()=>{

load();

constt=setInterval(()=>load(),REFRESH\_MS);// 每半小时自动刷新

return()=>clearInterval(t);

},\[load\]);

constadd=async()=>{

if(!/^\\d{6}$/.test(code.trim())){setErr("请输入 6 位股票代码");return;}

consts=parseFloat(shares),c=parseFloat(cost);

if(!(s>0)\|\|!Number.isFinite(c)){setErr("数量须大于 0，成本价请填数字（可为负）");return;}

setAdding(true);setErr(null);

try{

setData(awaitapi.addHolding(code.trim(),s,c));

setCode("");setShares("");setCost("");

}catch(e){

setErr(einstanceofApiError ? e.message : "添加失败");

}finally{

setAdding(false);

}

};

constremove=async(c: string)=>{

try{setData(awaitapi.removeHolding(c));}catch{/\\* ignore \*/}

};

constaddClose=async()=>{

if(!/^\\d{6}$/.test(cCode.trim())){setErr("清仓记录：请输入 6 位代码");return;}

constp=parseFloat(cPrice),s=parseFloat(cShares),c=parseFloat(cCost);

if(!cDate){setErr("请选清仓日期");return;}

if(!(p>0)\|\|!(s>0)\|\|!Number.isFinite(c)){setErr("清仓价 / 股数须大于 0，成本请填数字（可为负）");return;}

setClosing(true);setErr(null);

try{

setData(awaitapi.closePosition(cCode.trim(),cDate,p,s,c));

setCCode("");setCDate("");setCPrice("");setCShares("");setCCost("");

}catch(e){

setErr(einstanceofApiError ? e.message : "添加清仓记录失败");

}finally{

setClosing(false);

}

};

constremoveClosed=async(i: number)=>{

try{setData(awaitapi.removeClosed(i));}catch{/\\* ignore \*/}

};

constholdings=data?.holdings\|\|\[\];

consttotals=data?.totals;

constclosed=data?.closed\|\|\[\];

constaiContext=totals

? \`我的持仓（本地数据）：\\n\`+holdings.map((h)=>\`${h.name}(${h.code}) ${h.shares}股 成本${h.cost} 现价${h.price} 浮盈${h.pnl}(${h.pnl\_pct}%)\`).join("\\n")+

\`\\n汇总：市值${totals.market\_value} 总浮盈${totals.pnl}(${totals.pnl\_pct}%)\`

: "我的持仓：暂无记录。";

return(

<div>

<PageHeader

title="我的持仓"

subtitle="自己录、存在本地，实时看浮动盈亏"

actions={

<divclassName="flex items-center gap-2">

{holdings.length>0&&(

<AskAiButtoncontext={aiContext}label="让 AI 看我的持仓"

suggestions={\["我的持仓集中在哪些方向","结构上有什么风险","帮我梳理一下"\]}/>

)}

<buttononClick={()=>load(true)}disabled={refreshing}

className="inline-flex items-center gap-1.5 rounded-lg border border-border px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground disabled:opacity-50">

{refreshing ? <Loader2className="h-4 w-4 animate-spin"/> : <RefreshCwclassName="h-4 w-4"/>}

刷新

</button>

</div>

}

/>

<divclassName="mb-4 flex items-start gap-2 rounded-lg border border-success/25 bg-success/5 p-3 text-xs text-muted-foreground">

<ShieldCheckclassName="mt-0.5 h-4 w-4 shrink-0 text-success"/>

<span>持仓<bclassName="text-foreground">只存在你本地</b>，不上传、不进仓库。行情每半小时自动刷新，也可手动刷新。本产品不提供标的、不给建议，只帮你把自己的账理清楚。</span>

</div>

{/\\* 汇总 \*/}

{totals&&holdings.length>0&&(

<divclassName="mb-4 grid grid-cols-2 gap-3 sm:grid-cols-4">

{\[\
\
{k: "总市值",v: fmt(totals.market\_value),c: "text-foreground"},\
\
{k: "总成本",v: fmt(totals.cost),c: "text-foreground"},\
\
{k: "浮动盈亏",v: (totals.pnl>0 ? "+" : "")+fmt(totals.pnl),c: pnlColor(totals.pnl)},\
\
{k: "盈亏比例",v: (totals.pnl\_pct>0 ? "+" : "")+totals.pnl\_pct+"%",c: pnlColor(totals.pnl)},\
\
\].map((m)=>(

<GlassCardkey={m.k}className="p-3">

<pclassName="text-xs text-muted-foreground">{m.k}</p>

<pclassName={cn("mt-1 font-mono text-lg font-bold",m.c)}>{m.v}</p>

</GlassCard>

))}

</div>

)}

{/\\* 录入 \*/}

<GlassCardclassName="mb-4">

<h3className="mb-3 text-sm font-semibold">添加持仓</h3>

<divclassName="flex flex-wrap items-end gap-2">

<div>

<labelclassName="mb-1 block text-xs text-muted-foreground">股票代码</label>

<inputvalue={code}onChange={(e)=>setCode(e.target.value.replace(/\\D/g,"").slice(0,6))}placeholder="6 位代码"

className="w-28 rounded-lg border border-border bg-black/20 px-3 py-2 text-sm outline-none focus:border-primary/50"/>

</div>

<div>

<labelclassName="mb-1 block text-xs text-muted-foreground">数量（股）</label>

<inputvalue={shares}onChange={(e)=>setShares(e.target.value.replace(/\[^\\d.\]/g,""))}placeholder="如 100"

className="w-28 rounded-lg border border-border bg-black/20 px-3 py-2 text-sm outline-none focus:border-primary/50"/>

</div>

<div>

<labelclassName="mb-1 block text-xs text-muted-foreground">成本价</label>

<inputvalue={cost}onChange={(e)=>setCost(e.target.value.replace(/\[^\\d.-\]/g,"").replace(/(?!^)-/g,""))}placeholder="如 12.5，可负"

className="w-28 rounded-lg border border-border bg-black/20 px-3 py-2 text-sm outline-none focus:border-primary/50"/>

</div>

<buttononClick={add}disabled={adding}

className="inline-flex items-center gap-1.5 rounded-lg bg-primary/15 px-4 py-2 text-sm font-medium text-primary shadow-glow hover:bg-primary/25 disabled:opacity-50">

{adding ? <Loader2className="h-4 w-4 animate-spin"/> : <PlusclassName="h-4 w-4"/>} 添加

</button>

</div>

<pclassName="mt-2 text-\[11px\] text-muted-foreground/60">同一代码再次添加会按加权平均成本合并（加仓）。</p>

</GlassCard>

{err&&(

<divclassName="mb-4 flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/5 p-3 text-sm text-destructive">

<AlertCircleclassName="h-4 w-4 shrink-0"/>{err}

</div>

)}

{/\\* 持仓表 \*/}

<GlassCardglow>

<divclassName="mb-2 flex items-center justify-between">

<h3className="font-semibold">持仓明细</h3>

{data?.updated&&<spanclassName="text-xs text-muted-foreground/60">更新于 {data.updated}</span>}

</div>

{holdings.length===0 ? (

<pclassName="py-8 text-center text-sm text-muted-foreground/60">还没有持仓记录，用上面的表单添加一笔。</p>

) : (

<divclassName="overflow-x-auto">

<tableclassName="w-full text-sm">

<thead>

<trclassName="border-b border-border/50 text-left text-xs text-muted-foreground">

{\["名称","现价","数量","成本","市值","浮动盈亏","盈亏%",""\].map((h)=>(

<thkey={h}className="whitespace-nowrap px-2 py-2 font-medium">{h}</th>

))}

</tr>

</thead>

<tbody>

{holdings.map((h)=>(

<trkey={h.code}className="border-b border-border/30">

<tdclassName="px-2 py-2.5">

<spanclassName="font-medium">{h.name}</span>

<spanclassName="ml-1.5 font-mono text-xs text-muted-foreground/60">{h.code}</span>

</td>

<tdclassName="px-2 py-2.5 font-mono">{fmtPx(h.price)}</td>

<tdclassName="px-2 py-2.5 font-mono text-muted-foreground">{fmt(h.shares)}</td>

<tdclassName="px-2 py-2.5 font-mono text-muted-foreground">{fmtPx(h.cost)}</td>

<tdclassName="px-2 py-2.5 font-mono">{fmt(h.market\_value)}</td>

<tdclassName={cn("px-2 py-2.5 font-mono",pnlColor(h.pnl))}>{h.pnl>0 ? "+" : ""}{fmt(h.pnl)}</td>

<tdclassName={cn("px-2 py-2.5 font-mono",pnlColor(h.pnl))}>{h.pnl\_pct>0 ? "+" : ""}{h.pnl\_pct}%</td>

<tdclassName="px-2 py-2.5">

<buttononClick={()=>remove(h.code)}className="text-muted-foreground/50 hover:text-destructive"title="删除">

<Trash2className="h-3.5 w-3.5"/>

</button>

</td>

</tr>

))}

</tbody>

</table>

</div>

)}

</GlassCard>

{/\\* 清仓录入 \*/}

<GlassCardclassName="mb-4 mt-6">

<h3className="mb-3 text-sm font-semibold">添加清仓记录</h3>

<divclassName="flex flex-wrap items-end gap-2">

<div>

<labelclassName="mb-1 block text-xs text-muted-foreground">股票代码</label>

<inputvalue={cCode}onChange={(e)=>setCCode(e.target.value.replace(/\\D/g,"").slice(0,6))}placeholder="6 位代码"

className="w-24 rounded-lg border border-border bg-black/20 px-3 py-2 text-sm outline-none focus:border-primary/50"/>

</div>

<div>

<labelclassName="mb-1 block text-xs text-muted-foreground">清仓日期</label>

<inputtype="date"value={cDate}onChange={(e)=>setCDate(e.target.value)}

className="rounded-lg border border-border bg-black/20 px-3 py-2 text-sm outline-none focus:border-primary/50"/>

</div>

<div>

<labelclassName="mb-1 block text-xs text-muted-foreground">清仓价</label>

<inputvalue={cPrice}onChange={(e)=>setCPrice(e.target.value.replace(/\[^\\d.\]/g,""))}placeholder="卖出价"

className="w-24 rounded-lg border border-border bg-black/20 px-3 py-2 text-sm outline-none focus:border-primary/50"/>

</div>

<div>

<labelclassName="mb-1 block text-xs text-muted-foreground">股数</label>

<inputvalue={cShares}onChange={(e)=>setCShares(e.target.value.replace(/\[^\\d.\]/g,""))}placeholder="如 100"

className="w-24 rounded-lg border border-border bg-black/20 px-3 py-2 text-sm outline-none focus:border-primary/50"/>

</div>

<div>

<labelclassName="mb-1 block text-xs text-muted-foreground">买入成本</label>

<inputvalue={cCost}onChange={(e)=>setCCost(e.target.value.replace(/\[^\\d.-\]/g,"").replace(/(?!^)-/g,""))}placeholder="成本价，可负"

className="w-24 rounded-lg border border-border bg-black/20 px-3 py-2 text-sm outline-none focus:border-primary/50"/>

</div>

<buttononClick={addClose}disabled={closing}

className="inline-flex items-center gap-1.5 rounded-lg bg-primary/15 px-4 py-2 text-sm font-medium text-primary shadow-glow hover:bg-primary/25 disabled:opacity-50">

{closing ? <Loader2className="h-4 w-4 animate-spin"/> : <PlusclassName="h-4 w-4"/>} 记录

</button>

</div>

</GlassCard>

{/\\* 已清仓列表 \*/}

<divclassName="mb-2 flex items-center justify-between">

<h3className="text-sm font-semibold text-muted-foreground">已清仓</h3>

{closed.length>0&&data&&(

<spanclassName="text-sm">

已实现盈亏合计 <bclassName={cn("font-mono",pnlColor(data.realized\_pnl))}>{data.realized\_pnl>0 ? "+" : ""}{fmt(data.realized\_pnl)}</b>

</span>

)}

</div>

<GlassCard>

{closed.length===0 ? (

<pclassName="py-6 text-center text-sm text-muted-foreground/60">还没有清仓记录。卖出后在上面记一笔，作为已实现盈亏的历史。</p>

) : (

<divclassName="overflow-x-auto">

<tableclassName="w-full text-sm">

<thead>

<trclassName="border-b border-border/50 text-left text-xs text-muted-foreground">

{\["名称","清仓日期","清仓价","股数","成本","已实现盈亏","盈亏%",""\].map((h)=>(

<thkey={h}className="whitespace-nowrap px-2 py-2 font-medium">{h}</th>

))}

</tr>

</thead>

<tbody>

{closed.map((c,i)=>(

<trkey={i}className="border-b border-border/30">

<tdclassName="px-2 py-2.5">

<spanclassName="font-medium">{c.name}</span>

<spanclassName="ml-1.5 font-mono text-xs text-muted-foreground/60">{c.code}</span>

</td>

<tdclassName="px-2 py-2.5 font-mono text-muted-foreground">{c.date}</td>

<tdclassName="px-2 py-2.5 font-mono">{fmtPx(c.price)}</td>

<tdclassName="px-2 py-2.5 font-mono text-muted-foreground">{fmt(c.shares)}</td>

<tdclassName="px-2 py-2.5 font-mono text-muted-foreground">{fmtPx(c.cost)}</td>

<tdclassName={cn("px-2 py-2.5 font-mono",pnlColor(c.pnl))}>{c.pnl>0 ? "+" : ""}{fmt(c.pnl)}</td>

<tdclassName={cn("px-2 py-2.5 font-mono",pnlColor(c.pnl))}>{c.pnl\_pct>0 ? "+" : ""}{c.pnl\_pct}%</td>

<tdclassName="px-2 py-2.5">

<buttononClick={()=>removeClosed(i)}className="text-muted-foreground/50 hover:text-destructive"title="删除">

<Trash2className="h-3.5 w-3.5"/>

</button>

</td>

</tr>

))}

</tbody>

</table>

</div>

)}

</GlassCard>

<Disclaimer/>

</div>

);

}

You can’t perform that action at this time.