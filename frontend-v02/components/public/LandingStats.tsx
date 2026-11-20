import CountUp from "../motion/CountUp";

export default function LandingStats({ courses,tracks }: { courses:any[]; tracks:any[] }) {
  const hours=Math.round(courses.reduce((sum,c)=>sum+(Number(c.estimated_hours)||0),0));
  const free=courses.filter(c=>c.settings?.is_free===true||c.settings?.access_type==="free").length;
  const items=[
    {value:courses.length,label:"Published courses"},
    {value:tracks.length,label:"Learning tracks"},
    {value:free,label:"Free to start"},
    {value:hours,label:"Hours of learning",suffix:"+"},
  ].filter(item=>item.value>0);
  if(items.length<2) return null;
  return <section className="landing-wrap landing-stats-section" aria-label="Learnora at a glance"><div className="landing-stats" data-stagger>{items.map(item=><div className="landing-stat" key={item.label}><strong><CountUp value={item.value} suffix={item.suffix}/></strong><span>{item.label}</span></div>)}</div></section>;
}
