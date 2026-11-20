/** Decorative topic strip; accessible topic links remain in the learning-areas section. */
export default function TopicMarquee({ topics }: { topics:string[] }) {
  if (topics.length<4) return null;
  const row=topics.slice(0,12);
  return <div className="topic-marquee" aria-hidden="true"><div className="topic-marquee-track">{[...row,...row].map((topic,i)=><span className="pill" key={i}>{topic}</span>)}</div></div>;
}
