import { Children, cloneElement, isValidElement, type ReactElement, type ReactNode } from "react";

/** Wraps each word in a span while preserving nested accent elements. */
export function splitWords(node: ReactNode, counter = { i:0 }): ReactNode {
  return Children.map(node,child => {
    if (typeof child === "string") return child.split(/(\s+)/).map((part,k) => {
      if (!part) return null;
      if (/^\s+$/.test(part)) return part;
      return <span key={k} className="split-word" style={{ ["--i" as string]:counter.i++ }}>{part}</span>;
    });
    if (isValidElement(child)) {
      const el=child as ReactElement<{children?:ReactNode}>;
      return cloneElement(el,undefined,splitWords(el.props.children,counter));
    }
    return child;
  });
}
