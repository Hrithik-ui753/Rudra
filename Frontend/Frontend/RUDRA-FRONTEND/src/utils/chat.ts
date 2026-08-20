/** Remove legacy follow-up footer embedded in assistant message text */
export function stripFollowupFooter(text: string): string {
  const markers = ['---\n💡', '---\n**Suggested', 'Suggested Next Questions', '💡 **Suggested'];
  let cut = text.length;
  for (const m of markers) {
    const idx = text.indexOf(m);
    if (idx >= 0 && idx < cut) cut = idx;
  }
  return cut < text.length ? text.slice(0, cut).trim() : text;
}

export function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
