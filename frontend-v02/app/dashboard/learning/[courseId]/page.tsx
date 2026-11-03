import { redirect } from "next/navigation";

export default function LegacyLearningRoute({params}:{params:{courseId:string}}){
  redirect("/courses/"+encodeURIComponent(params.courseId));
}
