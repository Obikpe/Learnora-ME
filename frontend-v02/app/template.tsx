/** Re-mounts on navigation so each page can fade in without changing fixed-position containing blocks. */
export default function Template({ children }: { children: React.ReactNode }) {
  return <div className="page-enter">{children}</div>;
}
