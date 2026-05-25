import { SectionPage } from "../components/SectionPage";

export const metadata = {
  title: "HR · The AI Native",
  description: "HR 各模块如何被 AI 重构？",
};

export default function HRPage() {
  // HR module filter (招聘 / 绩效 / 学发 / 组织设计 / 薪酬 / 员工体验)
  // is deferred until items have explicit module tags. PRD §6.1 specifies
  // this filter; will be added once Step 3 classifier learns to emit module.
  return <SectionPage section="HR" />;
}
