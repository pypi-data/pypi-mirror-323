/*
pyodide-mkdocs-theme
Copyleft GNU GPLv3 🄯 2024 Frédéric Zinelli

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.
If not, see <https://www.gnu.org/licenses/>.
*/



import { jsLogger } from 'jsLogger'
import {
  textShortener,
  txtFormat,
  withPyodideAsyncLock,
 } from 'functools'
import { PyodideSectionsRunner } from "2-pyodideSectionsRunner-runner-pyodide"
import { RuntimeManager } from '1-runtimeManager-runtime-pyodide'











function getSelectionText(){
  // Code inspired by https://stackoverflow.com/questions/5379120/get-the-highlighted-selected-text

  let text = "";
  if(window.getSelection){
      text = _getWindowSelection()

  }else if(document.selection && document.selection.type != "Control") {
      console.warn("Unsupported copy from PMT terminal (fallback to default/simplified behavior).")
      text = document.selection.createRange().text;
  }

  // Just like usual, jQuery terminals are messing with the content, replacing spaces
  // with "\u00a0" characters... x/
  text = text.replace(/\u00a0/ug, " ")

  // Strip ONE trailing new line if present, because it belongs to the end of the current
  // line (hence, messing what the user actually wants... generally)
  text = text.replace(/\n$/, '')
  return text;
}





/**Extraction of text selection using the window.getSelection feature with its DocumentFragment
 * objects. These are sending complete DOM subtrees, so depending on what parts of the UI are
 * selected, the entry point and the depth of the tree to explore to find the leaf content may
 * differ.
 *
 * Terminal output/contents are organized in the following way (ignoring top levels elements):
 *
 *        div.terminal-wrapper
 *            ├── div.terminal-output                 // All older commands or feedback blocks
 *            │     ├── div[data-index]               // One block (aka, one older command, or one feedback block)
 *            │     ├── ...
 *            │     └── div[data-index]
 *            │           ├── div                     // That represents one single line in the block
 *            │           ├── ...
 *            │           └── div.cmd-end-line        // Always present. The class is a flag for jQ.terminals.
 *            │                 └── (various spans)
 *            │
 *            └── div.cmd                             // Current command element, where the user is typing
 *                └── div.cmd-wrapper                 // Current command element, where the user is typing
 *                      ├── span.cmd-prompt           // Always first. Either ">>> " or "... "
 *                      ├── div                       // One div per extra command line.
 *                      ├── ...
 *                      └── div.cmd-cursor-line       // Always present. The class is a flag for jQ.terminals.
 *                            └── (various spans)
 *
 * The DocumentFragment objects may at most overlap on both `div.terminal-output` and
 * `div.cmd-wrapper`.
 * */
const _getWindowSelection=()=>{
  // Using this approach instead of `window.getSelection().toString()`, because sometimes, this
  // would swallow _SOME_ line breaks. (too bad...! :rolleyes: )

  const extractTxtIfExists=(section, jRule, getPrompt=false)=>{
    let gotSome = false
    let iPrompt = -1
    let prompt  = ""
    if(getPrompt){
      iPrompt = copied.length
      prompt  = section.find("span.cmd-prompt").text()
    }

    section.find(jRule).each(function(){
      const content = this.innerText
      if(content){
        copied.push(content)
        gotSome = true
      }
    })

    if(prompt && copied[iPrompt]){
      copied[iPrompt] = prompt + copied[iPrompt]
    }
    return gotSome
  }

  /*
  NOTES:
    1. The use of DocumentFragment is a total mess... 'Couldn't understand why there are sometimes
       additional empty fragments, and moreover, why the fragments are NOT matching the original
       tree hierarchy: on "current multiline commands", the first line with the prompt is seen in
       the fragment of the "terminal-output" part... x/
    2. If the selection ends inside the prompt itself, it won't be copied. I'd say, "I'm ok with
       that", because, _MEH!!_...
  */
  const selection = window.getSelection()
  const copied = []

  for(let iR=0;iR<selection.rangeCount;iR++){
    const range   = selection.getRangeAt(iR)
    const section = $(range.cloneContents() )

    // Always attempt to extract both ways (output and/or command):
    if(
        extractTxtIfExists(section, 'div[data-index]>div')
      | extractTxtIfExists(section, 'div.cmd-wrapper>div', true)
    ) continue

    // In nothing so far, just extract divs, and possibly the prompt
    if(
      extractTxtIfExists(section, 'div', true)
    ) continue

    // Otherwise, this is a single line or part of it => just extract directly the text content
    const txt = section.text()
    if(txt) copied.push(txt)
  }
  return copied.join('\n')
}




















class _TerminalHandler extends PyodideSectionsRunner {

  constructor(id, callInit=true){
    super(id, false)
    this.terminal      = null     // jQuery.terminal object
    this.termWrapper   = null     // jQuery Html element
    this.termEnabled   = false    // Flag to enforce activation of the terminal (admonitions+tabbed troubles)
    this.isIsolated    = id.startsWith("term_only")
    this.cmdChunk      = ""               // SINGLE line command to run
    this.cmdOnTheRun   = ""               // Complete code of the currently written multiline command ("executed so far")
    this.cmdStack      = []               // Multiline commands to come yet (coming from a copy/paste)
    this.eraseCmdOnTheRunInPost = false   // Flag to erase this.cmdOnTheRun when needed, but in post section only (so that __USER_CMD__ stays consistent on user's side)
    this.joinTerminalLines = false        // UI button related (internal value)
    this.pyodideConsoleRunner = null      // Will be: this.runPyodideConsole.bind(this)
    if(callInit) this._init()
  }

  _init(){
    super._init()
    this.alreadyRanEnv = false    // Specific to terminals, but defined "for everyone"
  }


  /**Build a jQuery terminal and bind it to the underlying pyodide runtime.
   *
   * WARNING:  If this is an IdeEditorHandler, this.id is the id of the editor div, not
   *           the id of the terminal div ! (hence the use of the termId argument)
   * */
  build(termId=null){
    if(!termId) termId = this.id
    const jqTermId = '#' + termId

    LOGGER_CONFIG.ACTIVATE && jsLogger("[Terminal] - build " + jqTermId)

    this.buildAsyncPythonExecutors()

    const termOptions = {
      greetings: "",                            // Cancel terminal banner (welcome message),
      completionEscape: false,
      prompt: CONFIG.MSG.promptStart,
      outputLimit: this.stdoutCutOff,           // this.terminal.settings().outputLimit=value (to change dynamically)
      enabled: false,                           // GET RID OF THE DAMN AUTO-SCROLL!!!!!!
      // wrap: getWrapTerms(),                  // This also deactivate colors... FUCK THIS!
      keymap: this.getTerminalBindings(),
      completion: function(command, callback){  // terminal AUTO-completion
        const suggestionsArr = PyodideSectionsRunner.pyFuncs.complete(command)
        callback(suggestionsArr)
      },
      mousewheel: function(){ return true },    // Seems enough to fix the "no mouse wheel" troubles on terminals
      onBlur: function(){},                     // Allow to leave the textarea, focus-wise.
    }                                           // DO NOT PUT ANY CODE INSIDE THIS !! (I don't understand what's going
                                                // on here, but  this is the only way I found to make all this work...)

    this.terminal    = $(jqTermId).terminal(this.runnerTerm, termOptions)
    this.termWrapper = this.terminal.parent()

    this.terminal.history().clear()             // Clear the history from localeStorage.

    if(CONFIG._devMode) CONFIG.terms[termId]=this.terminal

    this.addEventToRunOnce(
      this.terminal, this.ensureTerminalActivationOnClick.bind(this), true
    )
    this.termWrapper.on(
      'click', this.attemptAtResolvingTerminalUiTroubles.bind(this)
    )
    this.termWrapper.find(".stdout-wraps-btn").on(
      'click', this.swapTerminalLinesJoinerForCopies.bind(this)
    )
    this.termWrapper.find(".stdout-ctrl").on(
      'click', _=>{ this.updateStdoutCutFeedback(!this.cutFeedback) }
    )
    this.updateStdoutCutFeedback(this.cutFeedback)

    this.prefillTermIfAny()

    super.build()   // Nothing done there so far, but for consistency...
  }



  /**Update the UI button status and the inner state of cutFeedback to the given value.
   * */
  updateStdoutCutFeedback(to){
    this.data.cut_feedback = CONFIG.cutFeedback = to
    const method = to ? 'removeClass' : 'addClass'
    $(this.termWrapper).find(".stdout-x-ray-svg")[method]('py_mk_hidden')
  }



  swapTerminalLinesJoinerForCopies(){
    this.joinTerminalLines = !this.joinTerminalLines
    const method = this.joinTerminalLines ? 'removeClass' : 'addClass'
    this.termWrapper.find(".stdout-wraps-btn")[method]('deactivated')
  }


  /**Because terminals are created deactivated, add an EventListener for click to reactivate them.
   * Using the async lock so that the user cannot resume a terminal while it's running (could
   * occur on first click/run).
   *
   * - Does nothing if the terminal already got activated by other means.
   * - If a selection exists, do not enable the terminal or the selection gets lost.
   * */
  ensureTerminalActivationOnClick(){
    if(!this.termEnabled){
      if(!getSelectionText()){
        this.terminal.focus(true)
        this.terminal.enable()
      }
      this.termEnabled = true
    }
  }


  /**Transfer user's resize operations to the terminal wrapper, so that the content stays
   * confined to the wrapping div.
   * */
  terminalAutoWidthOnResize(){
    const wrapperWidth = this.termWrapper.width()
    if(wrapperWidth != this.terminal.width()){
      this.terminal.width(wrapperWidth)
    }
  }


  /**This routine tries to fix the following bugs with terminals:
   *    - The 0px width terminals on tab change (markdown: `=== "tabbed"`):
   *    - The FILL content lost when the user changed of tab anywhere in the page...
   * */
  attemptAtResolvingTerminalUiTroubles(){
    const w = this.termWrapper.css('width')
    if(w != this.terminal.css('width')){
      this.terminal.css('width', w)
    }
    const h = this.termWrapper.css('height')
    if(h != this.terminal.css('height')){
      this.terminal.css('height', h)
    }

    // NOT NEEDED ANYMORE (...?)
    // if(this.isIsolated && this.prefillTerm && !this.terminal.get_command()){
    //   this.prefillTermIfAny()
    // }
  }


  /**Routine adding the given callback on a jQuery @target click event, with an automatic
   * "unsubscription on first click" wrapping logic.
   * If @withLock is true, the routine is using the Pyodide async lock, to avoid messing
   * with the global state of the page.
   * */
  addEventToRunOnce(target, cbk, withLock=false, event='click'){
    let clickHandler = async _=>{
      target.off(event, clickHandler)
      cbk()
    }
    if(withLock){
      clickHandler = withPyodideAsyncLock('term_'+event, clickHandler)
    }
    target.on(event, clickHandler)
  }



  /**Hook returning the configuration for terminal keyboard shortcuts bindings.
   * To override in child classes when needed.
   *
   * Handled here: transfer KeyInterrupt from DOM to python runtime (note: actually
   * useless as long as no worker used!).
   * */
  getTerminalBindings(){
    return ({
      "CTRL+C": async (e) => {

        // Skip if some text is selected (=> copy!)
        let txt = getSelectionText()
        if (txt) {
          e.preventDefault()
          e.stopPropagation()
          if(this.joinTerminalLines){
            txt = txt.replace(/\n/g, '')
          }
          await navigator.clipboard.writeText(txt)
          return
        }

        let currentCmd = this.terminal.get_command();
        PyodideSectionsRunner.pyFuncs.clear_console();
        this.terminal.echo(CONFIG.MSG.promptStart + currentCmd);
        this.terminal.echo(txtFormat.error("KeyboardInterrupt"));
        this.terminal.set_command("");
        this.terminal.set_prompt(CONFIG.MSG.promptStart);
      },
    })
  }


  buildAsyncPythonExecutors(){
    throw new Error('Should be overridden in the child class.')
  }


  prefillTermIfAny(){
    if(this.prefillTerm){
      const history = this.terminal.history()
      history.append(this.prefillTerm)
      this.terminal.set_command(this.prefillTerm)
    }
  }


  setupGlobalConfig(){
    super.setupGlobalConfig()
    CONFIG.cutFeedback = this.cutFeedback
    CONFIG.termMessage = this.termFeedbackFromPyodide.bind(this)
  }


  /**When a terminal is available, display stdout and errors in it, if any.
   *
   *  @format: by default `"error"`. Formatting to use for the jQuery.terminal.
   * If @format is `null`, the @content is already formatted for the terminal and no txtFormat
   * option must be applied anymore.
   * */
  giveFeedback(content, format='error'){
    if(content){
      if(format!==null) content = txtFormat[format](content)
      this.terminalEcho(content)
    }
  }


  /**Feedback coming from pyodide, one way or another...
   * Any call reaching this method is about a content to unconditionally show in the terminal.
   *
   * If @isPrint is true, the call comes from a print statement and is a stdout redirection.
   * the child method already decided if the message must be displayed or not.
   * If @isPrint is false, the call is a direct one to terminal_message, from an author or a user,
   * and the key argument has to match the STD_KEY argument
   *
   * @throws: Error if isPrint is false and the key isn't the expected one, of if the `format`
   *          option is unknown.
   */
  termFeedbackFromPyodide(_key, msg, format, isPrint=false, newline=false){
    if(!txtFormat[format]){
      throw new Error(`Unknown formatting option: ${format}`)
    }
    msg = textShortener(msg)
    this.terminalEcho(txtFormat[format](msg), {newline})
  }


  /**Internal hook, allowing to capture all the content sent to the terminal from a parent class
   * (aka, IdeTester...).
   * WARNING: at this point, the content is already formatted with jQuery.terminal syntaxes.
   * */
  terminalEcho(content, options){
    this.terminal.echo(content, options ?? {newline:true})
  }
}












export class TerminalRunner extends _TerminalHandler {


  /**Generate the async-locked callback used to run commands typed into the terminal.
   * */
  buildAsyncPythonExecutors(running=CONFIG.runningMode.cmd){

    this.runnerTerm = this.lockedRunnerWithBigFailWarningFactory(
      running,
      this.setupRuntimeTerminalCmd,
      this.runTermCommand,
      this.teardownRuntimeTerminalCmd,
    )
    this.pyodideConsoleRunner = this.runPyodideConsole.bind(this)
  }

  async applyAutoRun(){
    await this.runnerTerm(this.prefillTerm)
  }



  /**Definitions of @cmdChunk and @cmdOnThRun and general context about `PyodideConsole`:
   * ------------------------------------------------------------------------------------
   *
   *
   * All those properties, but especially @cmdChunk , are trickier than they seem.
   * This is essentially because the hidden/inner PyodideConsole is actually running totally
   * independently of the jQuery.terminal object itself.
   *
   * Concretely, the PyodideConsole is handling the code itself without troubles, but anything
   * other than "just run that code" (aka, installations/imports, exclusions, ...) still has to
   * be done around the console.
   *
   *
   * What a @cmdChunk means (brain-wise), might sometimes be quite different of what a terminal
   * might actually be sending here as argument:
   *
   * @cmdChunk: This is the string content that is passed through _WHEN THE USER HITS `Enter` in
   *           the terminal without holding Shift key_. This implies @cmdChunk could concretely
   *           be a lot of different things:
   *                - A single line command, just like you'd expect:
   *                      `a = 45+6`
   *                - A multiline command, potentially with several "commands" in it (two, here):
   *                      ```
   *                      globs = {}
   *                      def func(k):
   *                          return globs.get(k, 42)
   *                      ```
   *                - The CONTINUATION of a multiline command started earlier (here it gets messy):
   *                      Previously:   `>>> """ Starting the multi thing`
   *                      Previously:   `... continue it`
   *                      Now:          `... third line`
   *
   *                      After hitting `Enter`, @cmdChunk will be `"third line"` ONLY.
   *
   *                - Any mix of all these two last...
   * */
  async setupRuntimeTerminalCmd(cmdChunk){

    this.cmdChunk    = this._handleMultilineCommands(cmdChunk)
    this.cmdOnTheRun = !this.cmdOnTheRun ? this.cmdChunk : this.cmdOnTheRun + '\n' + this.cmdChunk
    this.storeUserCodeInPython('__USER_CMD__', this.cmdOnTheRun)
    this.terminal.pause()

    let runtime
    if(!this.alreadyRanEnv){
      // If an IDE/terminal is run before the IDE itself, it must run the env/post sections.
      runtime = await this.setupRuntimeTrackingEnvRun()

    }else{
      // If env already ran before, envTerm HAS to run independently, so remove the dependency.
      runtime = new RuntimeManager(this)
      runtime.changeDependency('envTerm', 'start')  // Make envTerm runnable on its own!
    }

    await this.setupRuntime(runtime, 'envTerm')
    return runtime
  }


  _handleMultilineCommands(cmd){
    const isMultiLines = cmd.includes('\n')
    if(!isMultiLines) return cmd

    const [first, ...cmds] = cmd.split('\n')

    // Hack the current last (multi-)line of the terminal and replace it with the first only,
    // then execute it without any additional display in the terminal:
    const prompt = this.terminal.get_prompt()
    this.terminal.update(-1, prompt+first)

    if(this.cmdStack.length) throw new Error(
      `Some multiline commands are already stored: a new multiline command should never occur.`
    )
    this.cmdStack = cmds.reverse()
    return first
  }


  /**Centralizing the logic to decide if the `env` section has been run or not.
   * */
  async setupRuntimeTrackingEnvRun(){
    const runtime = await this.setupRuntime()
    this.alreadyRanEnv = !runtime.stopped
    return runtime
  }



  /**Specific teardown steps when using a terminal command (isolated or IDE's terminal).
   * */
  async teardownRuntimeTerminalCmd(runtime){
    try{
      await runtime.runWithCtx('postTerm')

    }finally{
      // If ever postTerm failed, post might still have to run:
      await this.teardownRuntime(runtime)
      if(this.eraseCmdOnTheRunInPost) this.cmdOnTheRun = ""
    }

    // Triggers the next command line if a multiline command has been pasted.
    // this will be run only when the current executions are fully resumed (so that the Pyodide
    // lock has been released)
    if(this.cmdStack.length){
      setTimeout(async()=>await this.terminal.exec(this.cmdStack.pop()))
    }
  }


  /**Generic terminal teardown actions (common to isolated and IDEs' terminals)
   * */
  async teardownRuntime(runtime) {
    LOGGER_CONFIG.ACTIVATE && jsLogger("[CheckPoint] - TerminalRunner teardownRuntime")
    if(!this.cmdStack.length) this.terminal.resume()
    await super.teardownRuntime(runtime)              // Runs ONLY if `env` has also been run
    this.storeUserCodeInPython('__USER_CMD__', "")
  }





  /**Extract the current command from the terminal and:
   *  - either run it directly if it doesn't hold line breaks,
   *  - or split it and handle each line separately, to mimic the behavior of a true
   *    python terminal.
   * */
  async runTermCommand(runtime){
    LOGGER_CONFIG.ACTIVATE && jsLogger("[CheckPoint] - Terminal - start running command", this.cmdChunk)

    this.eraseCmdOnTheRunInPost = false

    if(runtime.stopped){
      LOGGER_CONFIG.ACTIVATE && jsLogger("[CheckPoint] - Terminal - Skipped!")
      this.eraseCmdOnTheRunInPost = true
      return
    }

    await runtime.runWithCtx({
      section: CONFIG.runningMode.cmd,
      code: this.cmdOnTheRun,
      isEnvSection: false,
      applyExclusionsIfAny: true,
      method: this.pyodideConsoleRunner,
      logConfig: {
        code: this.cmdOnTheRun,
        autoAssertExtraction: false,
        purgeTrace: runtime.purgeStackTrace
      },
    })

    // Needed if the error was raised on imports/exclusions. If the command itself rose, this
    // will just redo some steps for nothing...
    if(runtime.stopped){
      PyodideSectionsRunner.pyFuncs.clear_console()
      this.eraseCmdOnTheRunInPost = true
      this.terminal.set_prompt(CONFIG.MSG.promptStart)
    }
  }


  async runPyodideConsole(){
    let state='syntax-error'
    try{
      state = await PyodideSectionsRunner.pyFuncs.redirect_cmd(this.cmdChunk)

    }finally{
      const isIncomplete = state == 'incomplete'
      const prompt = isIncomplete ? CONFIG.MSG.promptWait : CONFIG.MSG.promptStart
      this.terminal.set_prompt(prompt)
      this.eraseCmdOnTheRunInPost = !isIncomplete
    }
  }
}


CONFIG.CLASSES_POOL.Terminal = TerminalRunner
