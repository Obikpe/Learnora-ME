"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";

/** Reset the document scroll position after every client-side route change. */
export default function RouteScrollReset() {
  const pathname = usePathname();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return null;
}
