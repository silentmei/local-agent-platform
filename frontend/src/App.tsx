import { FormEvent, useEffect, useState } from "react";
import {
  ChevronLeft,
  ChevronRight,
  Check,
  Clock3,
  FileText,
  Loader2,
  Play,
  RefreshCw,
  ShieldAlert,
  Sparkles,
  TerminalSquare,
  X,
} from "lucide-react";
import { approveTask, getTask, getTaskLogs, listTasks, submitTask } from "./api";
import type { StepLog, Task } from "./types";

const statusLabels: Record<string, string> = {
  completed: "已完成",
  pending_approval: "待审批",
  failed: "失败",
  rejected: "已拒绝",
  tool_selected: "已选工具",
  tool_executed: "已执行",
  approved: "已批准",
  created: "已创建",
};

function formatTime(value?: string) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date(value));
}

function statusTone(status: string) {
  if (status === "completed") return "success";
  if (status === "pending_approval") return "warning";
  if (status === "failed" || status === "rejected") return "danger";
  return "neutral";
}

function prettyJson(value: unknown) {
  if (value === null || value === undefined) return "";
  if (typeof value === "string") return value;
  return JSON.stringify(value, null, 2);
}

export default function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [logs, setLogs] = useState<StepLog[]>([]);
  const [taskText, setTaskText] = useState("读取 requirements.txt");
  const [detailCardIndex, setDetailCardIndex] = useState(0);
  const [logIndex, setLogIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isApproving, setIsApproving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function refreshTasks(selectTaskId?: number) {
    setIsLoading(true);
    setError(null);

    try {
      const nextTasks = await listTasks();
      setTasks(nextTasks);

      const nextSelected =
        nextTasks.find((task) => task.id === selectTaskId) ??
        (selectedTask ? nextTasks.find((task) => task.id === selectedTask.id) : undefined) ??
        nextTasks[0] ??
        null;

      if (nextSelected) {
        const [detail, nextLogs] = await Promise.all([
          getTask(nextSelected.id),
          getTaskLogs(nextSelected.id),
        ]);
        setSelectedTask(detail);
        setLogs(nextLogs);
      } else {
        setSelectedTask(null);
        setLogs([]);
      }
      setDetailCardIndex(0);
      setLogIndex(0);
    } catch (err) {
      setError(err instanceof Error ? err.message : "请求失败");
    } finally {
      setIsLoading(false);
    }
  }

  async function selectTask(taskId: number) {
    setIsLoading(true);
    setError(null);

    try {
      const [detail, nextLogs] = await Promise.all([getTask(taskId), getTaskLogs(taskId)]);
      setSelectedTask(detail);
      setLogs(nextLogs);
      setDetailCardIndex(0);
      setLogIndex(0);
    } catch (err) {
      setError(err instanceof Error ? err.message : "请求失败");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const text = taskText.trim();
    if (!text) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const payload = await submitTask(text);
      await refreshTasks(payload.task_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "任务提交失败");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleApproval(approved: boolean) {
    if (!selectedTask) return;

    setIsApproving(true);
    setError(null);

    try {
      const payload = await approveTask(selectedTask.id, approved);
      await refreshTasks(payload.task_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "审批失败");
    } finally {
      setIsApproving(false);
    }
  }

  useEffect(() => {
    void refreshTasks();
  }, []);

  const selectedStatus = selectedTask?.status ?? "created";
  const needsApproval = selectedTask?.status === "pending_approval";
  const detailCards = [
    { id: "result", label: "结果", icon: FileText },
    { id: "approval", label: "审批", icon: ShieldAlert },
    { id: "raw", label: "数据", icon: TerminalSquare },
  ];
  const activeDetailCard = detailCards[detailCardIndex] ?? detailCards[0];
  const ActiveDetailIcon = activeDetailCard.icon;
  const activeLog = logs[logIndex];

  return (
    <main className="shell">
      <section className="sidebar">
        <div className="brand">
          <div className="traffic" aria-hidden="true">
            <span className="red" />
            <span className="yellow" />
            <span className="green" />
          </div>
          <div>
            <p className="eyebrow">Local Agent</p>
            <h1>工作台</h1>
          </div>
        </div>

        <button className="refreshButton" onClick={() => refreshTasks()} disabled={isLoading}>
          <RefreshCw size={16} />
          刷新
        </button>

        <div className="taskList">
          {tasks.map((task) => (
            <button
              className={`taskItem ${selectedTask?.id === task.id ? "active" : ""}`}
              key={task.id}
              onClick={() => selectTask(task.id)}
            >
              <span className={`dot ${statusTone(task.status)}`} />
              <span className="taskCopy">
                <strong>{task.task}</strong>
                <small>
                  #{task.id} · {statusLabels[task.status] ?? task.status}
                </small>
              </span>
            </button>
          ))}
        </div>
      </section>

      <section className="workspace">
        <form className="composer" onSubmit={handleSubmit}>
          <div className="composerIcon">
            <Sparkles size={22} />
          </div>
          <textarea
            value={taskText}
            onChange={(event) => setTaskText(event.target.value)}
            placeholder="输入一个本地任务"
            rows={3}
          />
          <button className="primaryButton" disabled={isSubmitting || !taskText.trim()}>
            {isSubmitting ? <Loader2 className="spin" size={18} /> : <Play size={18} />}
            运行
          </button>
        </form>

        {error && <div className="errorBanner">{error}</div>}

        <div className="contentGrid">
          <section className="panel detailPanel">
            <div className="panelHeader">
              <div>
                <p className="eyebrow">Task</p>
                <h2>{selectedTask?.task ?? "暂无任务"}</h2>
              </div>
              <span className={`statusPill ${statusTone(selectedStatus)}`}>
                {statusLabels[selectedStatus] ?? selectedStatus}
              </span>
            </div>

            <div className="metaGrid">
              <div>
                <span>任务 ID</span>
                <strong>{selectedTask?.id ?? "-"}</strong>
              </div>
              <div>
                <span>工具</span>
                <strong>{selectedTask?.selected_tool ?? "-"}</strong>
              </div>
              <div>
                <span>更新时间</span>
                <strong>{formatTime(selectedTask?.updated_at)}</strong>
              </div>
            </div>

            <div className="cardSwitcher">
              {detailCards.map((card, index) => (
                <button
                  className={index === detailCardIndex ? "active" : ""}
                  key={card.id}
                  onClick={() => setDetailCardIndex(index)}
                  type="button"
                >
                  <card.icon size={15} />
                  {card.label}
                </button>
              ))}
            </div>

            <div className="flipCard">
              <div className="sectionTitle">
                <ActiveDetailIcon size={17} />
                <span>{activeDetailCard.label}</span>
              </div>

              {activeDetailCard.id === "result" && (
                <pre>{selectedTask?.final_response ?? "任务完成后会显示在这里。"}</pre>
              )}

              {activeDetailCard.id === "approval" && (
                <div className="approvalCard">
                  <div className="approvalText">
                    <ShieldAlert size={20} />
                    <span>
                      {needsApproval
                        ? selectedTask.approval_reason ?? "该操作需要审批"
                        : "当前任务不需要审批。"}
                    </span>
                  </div>

                  {needsApproval && (
                    <div className="approvalActions">
                      <button
                        className="secondaryButton"
                        onClick={() => handleApproval(false)}
                        disabled={isApproving}
                        type="button"
                      >
                        <X size={16} />
                        拒绝
                      </button>
                      <button
                        className="approveButton"
                        onClick={() => handleApproval(true)}
                        disabled={isApproving}
                        type="button"
                      >
                        {isApproving ? (
                          <Loader2 className="spin" size={16} />
                        ) : (
                          <Check size={16} />
                        )}
                        批准
                      </button>
                    </div>
                  )}
                </div>
              )}

              {activeDetailCard.id === "raw" && <pre>{prettyJson(selectedTask)}</pre>}
            </div>
          </section>

          <section className="panel logPanel">
            <div className="panelHeader compact">
              <div>
                <p className="eyebrow">Trace</p>
                <h2>执行日志</h2>
              </div>
              <Clock3 size={18} />
            </div>

            <div className="logPager">
              <button
                disabled={logs.length === 0 || logIndex === 0}
                onClick={() => setLogIndex((index) => Math.max(0, index - 1))}
                type="button"
              >
                <ChevronLeft size={16} />
              </button>
              <span>
                {logs.length === 0 ? "0 / 0" : `${logIndex + 1} / ${logs.length}`}
              </span>
              <button
                disabled={logs.length === 0 || logIndex === logs.length - 1}
                onClick={() => setLogIndex((index) => Math.min(logs.length - 1, index + 1))}
                type="button"
              >
                <ChevronRight size={16} />
              </button>
            </div>

            <div className="timeline single">
              {logs.length === 0 && <p className="empty">暂无日志</p>}
              {activeLog && (
                <article className="logItem featured" key={activeLog.id}>
                  <span className={`timelineDot ${statusTone(activeLog.status)}`} />
                  <div>
                    <div className="logHead">
                      <strong>{activeLog.node}</strong>
                      <small>{formatTime(activeLog.created_at)}</small>
                    </div>
                    <p>{activeLog.message}</p>
                    <span className="logStatus">{activeLog.status}</span>
                  </div>
                </article>
              )}
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}
