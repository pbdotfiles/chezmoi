// Reports the state of the sessions open in this TUI to tmux, so the status bar
// can mark each window. Colors and the hook that clears "done" live in ~/.tmux.conf.
//
//   pane option   @oc_state  blocked | working | idle
//   window option @oc_done   1 when a run finished while nobody was viewing the window
//
// Does nothing outside tmux.
import { Plugin } from "@opencode/plugin/tui"
import { execFile, execFileSync } from "node:child_process"

type State = "blocked" | "working" | "idle"
type Root = { id: string; busy: boolean; attention: boolean }

export default Plugin.define({
  id: "paul.tmux-status",
  setup(ctx) {
    const pane = process.env.TMUX_PANE
    if (!process.env.TMUX || !pane) return

    const running = new Set<string>() // executing session IDs, roots or subagents
    const pending = new Map<string, string>() // permission or form ID -> session ID
    const wasBusy = new Map<string, boolean>() // root session ID -> busy at last check
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

    const root = (sessionID: string) => {
      try {
        return ctx.data.session.root(sessionID)
      } catch {
        return sessionID
      }
    }

    // Root sessions shown by this TUI: its tabs, or the current session when tabs are off.
    const openRoots = (): Root[] => {
      try {
        if (ctx.ui.tabs.enabled()) {
          const tabs = ctx.ui.tabs.list()
          if (tabs.length > 0) return tabs.map((t) => ({ id: t.sessionID, busy: t.busy, attention: t.attention }))
        }
        const route = ctx.ui.router.current()
        if (route.type === "session") return [{ id: root(route.sessionID), busy: false, attention: false }]
      } catch {}
      return []
    }

    const check = () => {
      const roots = openRoots()
      const runningRoots = new Set([...running].map(root))
      const pendingRoots = new Set([...pending.values()].map(root))
      let blocked = false
      let working = false
      let finished = false

      for (const r of roots) {
        const isBlocked = r.attention || pendingRoots.has(r.id)
        const isBusy = r.busy || runningRoots.has(r.id)
        if (isBlocked) blocked = true
        else if (isBusy) working = true
        if (wasBusy.get(r.id) && !isBusy && !isBlocked) finished = true
        wasBusy.set(r.id, isBusy || isBlocked)
      }
      const open = new Set(roots.map((r) => r.id))
      for (const id of wasBusy.keys()) if (!open.has(id)) wasBusy.delete(id)

      if (finished) {
        enqueue(async () => {
          // Only mark "done" when no client is currently viewing this window.
          if ((await tmux("display", "-p", "-t", pane, "#{window_active_clients}")) === "0")
            await tmux("set", "-w", "-t", pane, "@oc_done", "1")
        })
      }

      const state: State = blocked ? "blocked" : working ? "working" : "idle"
      if (state !== written) {
        written = state
        enqueue(() => tmux("set", "-p", "-t", pane, "@oc_state", state))
      }
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

    // Also catches tab opens, closes and switches, which do not arrive as server events.
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
