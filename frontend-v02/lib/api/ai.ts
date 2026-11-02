import{request}from"./client";
export type AILearningContext={course_id:string;lesson_id:string;assessment_id?:string};
export const askAI=(message:string,feature="tutor",conversation_id?:string,context?:AILearningContext)=>request<any>("/ai/ask",{method:"POST",body:JSON.stringify({message,feature,conversation_id,...(context||{})})});
export const conversations=()=>request<any>("/ai/conversations");
export const conversation=(id:string)=>request<any>("/ai/conversations/"+encodeURIComponent(id));
export const archiveConversation=(id:string)=>request<any>("/ai/conversations/"+encodeURIComponent(id)+"/archive",{method:"POST"});
export const aiUsage=()=>request<any>("/ai/usage");
