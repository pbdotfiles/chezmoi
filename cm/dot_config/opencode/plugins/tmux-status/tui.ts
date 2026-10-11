// Reports the state of the session displayed in this TUI to tmux, so the status bar
// can mark each window. Colors and the hook that clears "done" live in ~/.tmux.conf.
//
//   pane option   @oc_state  blocked | working | idle
//   window option @oc_done   1 when the displayed session finished while nobody was viewing the window
//
// Only the displayed session counts. Background tabs are not tracked: with tabs.scope "cwd",
// every TUI started in the same folder shares one tab list, so tabs say nothing about a window.
// Does nothing outside tmux.
import { Plugin } from "@opencode/plugin/tui"
import { execFile, execFileSync } from "node:child_process"

type State = "blocked" | "working" | "idle"

export default Plugin.define({
  id: "paul.tmux-status",
  setup(ctx) {
    const pane = process.env.TMUX_PANE
    if (!process.env.TMUX || !pane) return

    const running = new Set<string>() // executing session IDs, roots or subagents
    const pending = new Map<string, string>() // permission or form ID -> session ID
    let last: { id: string; busy: boolean } | undefined // displayed root at last check
    let written: State | undefined
    let queue: Promise<unknown> = Promise.resolve()
    let debounce: ReturnType<typeof setTimeout> | undefined

    const tmux = (...args: string[]) =>
      new Promise<string>((resolve) =>
        execFile("tmux", args, { timeout: 2000 }, (error, stdout) => resolve(error ? "" : stdout.trim())),
      )
    const enqueue = (task: () => Promise<unknown>) => {
      queue = queue.then(task).catch(() => {})
    }
    const safe = <T>(read: () => T, fallback: T): T => {
      try {
        return read() ?? fallback
      } catch {
        return fallback
      }
    }

    // Root of the session on screen, so a subagent view counts as its parent session.
    const displayed = (): string | undefined => {
      const route = safe(() => ctx.ui.router.current(), undefined)
      if (route?.type !== "session") return undefined
      return safe(() => ctx.data.session.root(route.sessionID), route.sessionID)
    }

    const check = () => {
      const id = displayed()
      if (!id) {
        last = undefined
        return write("idle")
      }

      const family = new Set([id, ...safe(() => ctx.data.session.family(id), [] as string[])])
      const tab = safe(() => ctx.ui.tabs.list(), []).find((t) => t.sessionID === id)
      const members = [...family]

      const isBlocked =
        tab?.attention === true ||
        [...pending.values()].some((sessionID) => family.has(sessionID)) ||
        members.some((m) => safe(() => ctx.data.session.permission.list(m)?.length ?? 0, 0) > 0) ||
        members.some((m) => safe(() => ctx.data.session.form.list(m)?.length ?? 0, 0) > 0)
      const isBusy =
        tab?.busy === true ||
        members.some((m) => running.has(m)) ||
        members.some((m) => safe(() => ctx.data.session.status(m), "idle") === "running")

      // "Done" only when the same session goes from busy to settled, not when switching sessions.
      if (last?.id === id && last.busy && !isBusy && !isBlocked) {
        enqueue(async () => {
          // Only mark "done" when no client is currently viewing this window.
          if ((await tmux("display", "-p", "-t", pane, "#{window_active_clients}")) === "0")
            await tmux("set", "-w", "-t", pane, "@oc_done", "1")
        })
      }
      last = { id, busy: isBusy || isBlocked }

      write(isBlocked ? "blocked" : isBusy ? "working" : "idle")
    }

    const write = (state: State) => {
      if (state === written) return
      written = state
      enqueue(() => tmux("set", "-p", "-t", pane, "@oc_state", state))
    }

    const schedule = () => {
      clearTimeout(debounce)
      debounce = setTimeout(check, 100)
    }

    const stop = ctx.data.listen(({ details: event }) => {
      switch (event.type) {
        case "session.execution.started":
          running.add(event.data.sessionID)
          break
        case "session.execution.succeeded":
        case "session.execution.failed":
        case "session.execution.interrupted":
          running.delete(event.data.sessionID)
          for (const [id, sessionID] of pending) if (sessionID === event.data.sessionID) pending.delete(id)
          break
        case "permission.asked":
          pending.set(event.data.id, event.data.sessionID)
          break
        case "permission.replied":
          pending.delete(event.data.requestID)
          break
        case "form.created":
          pending.set(event.data.form.id, event.data.form.sessionID)
          break
        case "form.replied":
        case "form.cancelled":
          pending.delete(event.data.id)
          break
        default:
          return
      }
      schedule()
    })

    // Also catches switching to another session, which does not arrive as a server event.
    const timer = setInterval(check, 2000)
    check()

    const clear = () => {
      try {
        execFileSync("tmux", ["set", "-p", "-t", pane, "-u", "@oc_state"], { timeout: 1000, stdio: "ignore" })
      } catch {}
    }
    process.once("exit", clear)

    return () => {
      stop()
      clearInterval(timer)
      clearTimeout(debounce)
      process.off("exit", clear)
      clear()
    }
  },
})
