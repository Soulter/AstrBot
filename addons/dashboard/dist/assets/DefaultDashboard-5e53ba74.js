import{y as R,p as u,o as _,c as f,w as e,a as t,O as w,b as s,d as p,j as $,P as I,q as z,Q as F,z as S,s as O,F as M,u as j,n as x,r as U,l as V,e as y,t as h,S as b,T as W,D as N,U as C,W as X,X as D,Y as G,Z as L,V as k,f as m,G as H,_ as Y}from"./index-a328f13b.js";import{_ as P}from"./_plugin-vue_export-helper-c27b6911.js";import{a as q}from"./axios-21b846bc.js";const A={class:"d-flex align-start mb-6"},E={class:"ml-auto z-1"},Q={class:"text-h1 font-weight-medium"},Z=s("span",{class:"text-subtitle-1 text-medium-emphasis text-white"},"消息总数",-1),J={name:"TotalMessage",components:{},props:["stat"],watch:{stat:{handler:function(a,l){this.message_total=a.message_total},deep:!0}},data:()=>({message_total:0}),mounted(){}},K=Object.assign(J,{setup(a){const l=R([{title:"移除",icon:W}]);return(n,i)=>{const o=u("DotsIcon");return _(),f(b,{elevation:"0",class:"bg-secondary overflow-hidden bubble-shape bubble-secondary-shape"},{default:e(()=>[t(w,null,{default:e(()=>[s("div",A,[t(p,{icon:"",rounded:"sm",color:"darksecondary",variant:"flat"},{default:e(()=>[t($,{icon:"mdi-message"})]),_:1}),s("div",E,[t(I,{"close-on-content-click":!1},{activator:e(({props:c})=>[t(p,z({icon:"",rounded:"sm",color:"secondary",variant:"flat",size:"small"},c),{default:e(()=>[t(o,{"stroke-width":"1.5",width:"20"})]),_:2},1040)]),default:e(()=>[t(F,{rounded:"md",width:"150",class:"elevation-10"},{default:e(()=>[t(S,{density:"compact"},{default:e(()=>[(_(!0),O(M,null,j(l.value,(c,r)=>(_(),f(x,{key:r,value:r},{prepend:e(()=>[(_(),f(U(c.icon),{"stroke-width":"1.5",size:"20"}))]),default:e(()=>[t(V,{class:"ml-2"},{default:e(()=>[y(h(c.title),1)]),_:2},1024)]),_:2},1032,["value"]))),128))]),_:1})]),_:1})]),_:1})])]),s("h2",Q,h(n.message_total),1),Z]),_:1})]),_:1})}}}),tt={class:"d-flex align-start mb-3"},et={class:"ml-auto z-1"},at={class:"text-h1 font-weight-medium"},st=s("span",{class:"text-subtitle-1 text-medium-emphasis text-white"},"会话总数",-1),ot={class:"text-h1 font-weight-medium"},lt=s("span",{class:"text-subtitle-1 text-medium-emphasis text-white"},"会话总数",-1),nt={name:"TotalSession",components:{},props:["stat"],watch:{stat:{handler:function(a,l){this.session_total=a.session_total},deep:!0}},data:()=>({session_total:0}),mounted(){}},it=Object.assign(nt,{setup(a){const l=N("1"),n=C(()=>({chart:{type:"bar",height:90,fontFamily:"inherit",foreColor:"#a1aab2",sparkline:{enabled:!0}},dataLabels:{enabled:!1},colors:["#fff"],fill:{type:"solid",opacity:1},stroke:{curve:"smooth",width:3},yaxis:{min:0,max:100},tooltip:{theme:"dark",fixed:{enabled:!1},x:{show:!1},y:{title:{formatter:()=>"会话总数"}},marker:{show:!1}}})),i={series:[{name:"series1",data:[45,66,41,89,25,44,9,54]}]},o=C(()=>({chart:{type:"bar",height:90,fontFamily:"inherit",foreColor:"#a1aab2",sparkline:{enabled:!0}},dataLabels:{enabled:!1},colors:["#fff"],fill:{type:"solid",opacity:1},stroke:{curve:"smooth",width:3},yaxis:{min:0,max:100},tooltip:{theme:"dark",fixed:{enabled:!1},x:{show:!1},y:{title:{formatter:()=>"会话总数"}},marker:{show:!1}}})),c={series:[{name:"series1",data:[35,44,9,54,45,66,41,69]}]};return(r,d)=>{const g=u("apexchart");return _(),f(b,{elevation:"0",class:"bg-primary overflow-hidden bubble-shape bubble-primary-shape"},{default:e(()=>[t(w,null,{default:e(()=>[s("div",tt,[t(p,{icon:"",rounded:"sm",color:"darkprimary",variant:"flat"},{default:e(()=>[t($,{icon:"mdi-account-multiple-outline"})]),_:1}),s("div",et,[t(X,{modelValue:l.value,"onUpdate:modelValue":d[0]||(d[0]=v=>l.value=v),class:"theme-tab",density:"compact",end:""},{default:e(()=>[t(D,{value:"1","hide-slider":"",color:"transparent"},{default:e(()=>[y("按日")]),_:1}),t(D,{value:"2","hide-slider":"",color:"transparent"},{default:e(()=>[y("按月")]),_:1})]),_:1},8,["modelValue"])])]),t(G,{modelValue:l.value,"onUpdate:modelValue":d[1]||(d[1]=v=>l.value=v),class:"z-1"},{default:e(()=>[t(L,{value:"1"},{default:e(()=>[t(k,null,{default:e(()=>[t(m,{cols:"6"},{default:e(()=>[s("h2",at,h(r.session_total),1),st]),_:1}),t(m,{cols:"6"},{default:e(()=>[t(g,{type:"line",height:"90",options:n.value,series:i.series},null,8,["options","series"])]),_:1})]),_:1})]),_:1}),t(L,{value:"2"},{default:e(()=>[t(k,null,{default:e(()=>[t(m,{cols:"6"},{default:e(()=>[s("h2",ot,h(r.session_total),1),lt]),_:1}),t(m,{cols:"6"},{default:e(()=>[t(g,{type:"line",height:"90",options:o.value,series:c.series},null,8,["options","series"])]),_:1})]),_:1})]),_:1})]),_:1},8,["modelValue"])]),_:1})]),_:1})}}}),rt={name:"OnlineTime",components:{},props:["stat"],watch:{stat:{handler:function(a,l){this.memory=a.sys_perf.memory,this.runtime_str=a.sys_start_time;let n=new Date().getTime(),i=new Date(a.sys_start_time*1e3).getTime(),o=n-i,c=Math.floor(o/(24*3600*1e3)),r=o%(24*3600*1e3),d=Math.floor(r/(3600*1e3)),g=r%(3600*1e3),v=Math.floor(g/(60*1e3)),T=g%(60*1e3),B=Math.round(T/1e3);this.runtime_str=c+"天"+d+"小时"+v+"分"+B+"秒"},deep:!0}},data:()=>({_stat:{},memory:"Loading",runtime_str:"Loading"}),mounted(){}},dt={class:"d-flex align-center gap-3"},ct={class:"text-h4 font-weight-medium"},ut=s("span",{class:"text-subtitle-2 text-medium-emphasis text-white"},"运行时间",-1),mt={class:"d-flex align-center gap-3"},_t={class:"text-h4 font-weight-medium"},ht=s("span",{class:"text-subtitle-2 text-disabled font-weight-medium"},"占用内存",-1);function ft(a,l,n,i,o,c){return _(),O(M,null,[t(b,{elevation:"0",class:"bg-primary overflow-hidden bubble-shape-sm bubble-primary mb-6"},{default:e(()=>[t(w,{class:"pa-5"},{default:e(()=>[s("div",dt,[t(p,{color:"darkprimary",icon:"",rounded:"sm",variant:"flat"},{default:e(()=>[t($,{icon:"mdi-clock"})]),_:1}),s("div",null,[s("h4",ct,h(a.runtime_str),1),ut]),t(H),s("div",null,[t(p,{icon:"",rounded:"sm",variant:"plain"},{default:e(()=>[t($,{color:"black",icon:"mdi-stop",size:"32"})]),_:1})])])]),_:1})]),_:1}),t(b,{elevation:"0",class:"bubble-shape-sm overflow-hidden bubble-warning"},{default:e(()=>[t(w,{class:"pa-5"},{default:e(()=>[s("div",mt,[t(p,{color:"lightwarning",icon:"",rounded:"sm",variant:"flat"},{default:e(()=>[t($,{icon:"mdi-memory"})]),_:1}),s("div",null,[s("h4",_t,h(a.memory)+" MiB",1),ht])])]),_:1})]),_:1})],64)}const pt=P(rt,[["render",ft]]),bt=s("span",{class:"text-subtitle-2 text-disabled font-weight-bold"},"上行消息总趋势",-1),gt={class:"text-h3 mt-1"},vt={class:"mt-4"},yt={name:"MessageStat",components:{},props:["stat"],data:()=>({total_cnt:0,select:{state:"Today",abbr:"FL"},items:[{state:"过去 24 小时",abbr:"FL"},{state:"更多维度待开发喵!",abbr:"GA"}],chartOptions1:{chart:{type:"bar",height:400,fontFamily:"inherit",foreColor:"#a1aab2",stacked:!0},colors:["#1e88e5","#5e35b1","#ede7f6"],responsive:[{breakpoint:400,options:{legend:{position:"bottom",offsetX:-10,offsetY:0}}}],plotOptions:{bar:{horizontal:!1,columnWidth:"50%"}},xaxis:{type:"category",categories:[]},legend:{show:!0,fontFamily:"'Roboto', sans-serif",position:"bottom",offsetX:20,labels:{useSeriesColors:!1},markers:{width:16,height:16,radius:5},itemMargin:{horizontal:15,vertical:8}},fill:{type:"solid"},dataLabels:{enabled:!1},grid:{show:!0},tooltip:{theme:"dark"}},lineChart1:{series:[{name:"消息条数",data:[]}]}}),watch:{stat:{handler:function(a,l){let n=[],i=[];for(let o=0;o<a.message.length;o++){let c=new Date(a.message[o][0]*1e3),r=c.getHours(),d=c.getMinutes();d=d<10?"0"+d:d,n.push(r+":"+d),i.push(a.message[o][1]),this.total_cnt+=a.message[o][1]}this.$refs.rtchart.updateOptions({xaxis:{categories:n},series:[{data:i}]})},deep:!0}},mounted(){}},wt=Object.assign(yt,{setup(a){return(l,n)=>{const i=u("apexchart");return _(),f(b,{elevation:"0"},{default:e(()=>[t(b,{variant:"outlined"},{default:e(()=>[t(w,null,{default:e(()=>[t(k,null,{default:e(()=>[t(m,{cols:"12",sm:"9"},{default:e(()=>[bt,s("h3",gt,h(l.total_cnt),1)]),_:1}),t(m,{cols:"12",sm:"3"},{default:e(()=>[t(Y,{color:"primary",variant:"outlined","hide-details":"",modelValue:l.select,"onUpdate:modelValue":n[0]||(n[0]=o=>l.select=o),items:l.items,"item-title":"state","item-value":"abbr",label:"Select","persistent-hint":"","return-object":"","single-line":""},null,8,["modelValue","items"])]),_:1})]),_:1}),s("div",vt,[t(i,{type:"bar",height:"280",options:l.chartOptions1,series:l.lineChart1.series,ref:"rtchart"},null,8,["options","series"])])]),_:1})]),_:1})]),_:1})}}}),xt={class:"d-flex align-center"},$t=s("h4",{class:"text-h4 mt-1"},"各平台上行消息数",-1),Vt={class:"ml-auto"},kt={class:"mt-4"},Tt={class:"d-inline-flex align-center justify-space-between w-100"},St={class:"text-subtitle-1 text-medium-emphasis font-weight-bold"},Ct={class:"ml-auto text-subtitle-1 text-medium-emphasis font-weight-bold"},Ot={class:"text-center mt-3"},Mt={name:"PlatformStat",components:{},props:["stat"],watch:{stat:{handler:function(a,l){let n={};for(let i=0;i<a.platform.length;i++){const o=a.platform[i];n[o[1]]?n[o[1]]+=o[2]:n[o[1]]=o[2]}this.platforms=[];for(const i in n)if(Object.hasOwnProperty.call(n,i)){const o=n[i];this.platforms.push({name:i,count:o})}},deep:!0}},data:()=>({platforms:[]}),mounted(){}},Dt=Object.assign(Mt,{setup(a){return C(()=>({chart:{type:"area",height:95,fontFamily:"inherit",foreColor:"#a1aab2",sparkline:{enabled:!0}},colors:["#5e35b1"],dataLabels:{enabled:!1},stroke:{curve:"smooth",width:1},tooltip:{theme:"dark",fixed:{enabled:!1},x:{show:!1},y:{title:{formatter:()=>"消息条数 "}},marker:{show:!1}}})),(l,n)=>{const i=u("DotsIcon"),o=u("perfect-scrollbar"),c=u("ChevronRightIcon");return _(),f(b,{elevation:"0"},{default:e(()=>[t(b,{variant:"outlined"},{default:e(()=>[t(w,null,{default:e(()=>[s("div",xt,[$t,s("div",Vt,[t(I,{transition:"slide-y-transition"},{activator:e(({props:r})=>[t(p,z({color:"primary",size:"small",icon:"",rounded:"sm",variant:"text"},r),{default:e(()=>[t(i,{"stroke-width":"1.5",width:"25"})]),_:2},1040)]),default:e(()=>[t(F,{rounded:"md",width:"150",class:"elevation-10"},{default:e(()=>[t(S,null,{default:e(()=>[t(x,{value:"1"},{default:e(()=>[t(V,null,{default:e(()=>[y("今天")]),_:1})]),_:1}),t(x,{value:"2"},{default:e(()=>[t(V,null,{default:e(()=>[y("今月")]),_:1})]),_:1}),t(x,{value:"3"},{default:e(()=>[t(V,null,{default:e(()=>[y("今年")]),_:1})]),_:1})]),_:1})]),_:1})]),_:1})])]),s("div",kt,[t(o,{style:{height:"270px"}},{default:e(()=>[t(S,{lines:"two",class:"py-0"},{default:e(()=>[(_(!0),O(M,null,j(l.platforms,(r,d)=>(_(),f(x,{key:d,value:r,color:"secondary",rounded:"sm"},{default:e(()=>[s("div",Tt,[s("div",null,[s("h6",St,h(r.name),1)]),s("div",Ct,h(r.count)+" 条",1)])]),_:2},1032,["value"]))),128))]),_:1})]),_:1}),s("div",Ot,[t(p,{color:"primary",variant:"text"},{append:e(()=>[t(c,{"stroke-width":"1.5",width:"20"})]),default:e(()=>[y("详情 ")]),_:1})])])]),_:1})]),_:1})]),_:1})}}}),Lt={name:"DefaultDashboard",components:{TotalMessage:K,TotalSession:it,OnlineTime:pt,MessageStat:wt,PlatformStat:Dt},data:()=>({stat:{}}),mounted(){q.get("/api/stats").then(a=>{console.log("stat",a.data.data),this.stat=a.data.data})}};function It(a,l,n,i,o,c){const r=u("TotalMessage"),d=u("TotalSession"),g=u("OnlineTime"),v=u("MessageStat"),T=u("PlatformStat");return _(),f(k,null,{default:e(()=>[t(m,{cols:"12",md:"4"},{default:e(()=>[t(r,{stat:a.stat},null,8,["stat"])]),_:1}),t(m,{cols:"12",md:"4"},{default:e(()=>[t(d,{stat:a.stat},null,8,["stat"])]),_:1}),t(m,{cols:"12",md:"4"},{default:e(()=>[t(g,{stat:a.stat},null,8,["stat"])]),_:1}),t(m,{cols:"12",lg:"8"},{default:e(()=>[t(v,{stat:a.stat},null,8,["stat"])]),_:1}),t(m,{cols:"12",lg:"4"},{default:e(()=>[t(T,{stat:a.stat},null,8,["stat"])]),_:1})]),_:1})}const Pt=P(Lt,[["render",It]]);export{Pt as default};