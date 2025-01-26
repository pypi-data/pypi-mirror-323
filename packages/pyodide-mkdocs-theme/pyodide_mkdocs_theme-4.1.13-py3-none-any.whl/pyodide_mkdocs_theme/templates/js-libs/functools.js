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





export function getTheme(){
    // automatically load current palette
    const palette = __md_get("__palette")
    let curPalette = palette === null ? CONFIG.ACE_COLOR_THEME.customThemeDefaultKey
        : palette.color["scheme"]

    const style = CONFIG.ACE_COLOR_THEME.customTheme[curPalette]
    return "ace/theme/" + CONFIG.ACE_COLOR_THEME.aceStyle[style];
}




/**Randomly pick a value from an array.
 * @throws Error if the array is empty.
 * */
export function choice(arr){
    if(!arr.length){
        throw new Error("Cannot pick from an empty array")
    }
    const i = Math.random() * arr.length | 0
    return arr[i]
}




/**Async sleep (time given in milliseconds / must be awaited by the caller)
 * */
export function sleep(ms=0){
    return new Promise((resolve) => setTimeout(resolve, ms));
}




/**Create a global async Lock logistic, so that functions/methods involving pyodide will
 * not be able to run concurrently. The Lock value is a simple boolean flag, since the app
 * is single threaded, and its value is protected be defining it within a scope where the
 * "locking" function is also defined (behaves like a python/TS decorator. Kinda... :p ).
 * */
export const withPyodideAsyncLock = (_=>{

    /**Everything is run async but single threaded, so a global lock can be added, using a simple
     * boolean flag, declared inside a closure to avoid a user messing with the variable...
     * */
    let pyodideLocked = false


    /**Function factory ("decorator like"), managing the global pyodide lock.
     * If a call is done while pyodide is locked, it is delayed until the lock is available.
     *
     * @name: Logging purpose only
     *
     * @asyncCallback: async function or method to wrap with the Lock. The calls are:
     *      - Passing in the current `@this` context.
     *      - And ofc the arguments (any number)
     * */
    return function withPyodideAsyncLock(name, asyncCallback){
        const logName = asyncCallback.name || name

        const wrapper = async function(...args){
            await waitForPyodideReady()

            LOGGER_CONFIG.ACTIVATE && jsLogger("[LOCK?] -", logName, pyodideLocked)
            while(pyodideLocked){
                await sleep(60)
            }
            pyodideLocked = true
            LOGGER_CONFIG.ACTIVATE && jsLogger("[LOCK ACQUIRE] -", logName)
            let ret;
            try{
                ret = await asyncCallback.apply(this, args)
            }catch(e){
                console.error(e)
                    // Always keep that to be warned when something goes wrong, otherwise
                    // errors in JS are just swallowed (impossible to rethrow them, because
                    // of the async context).
            }finally{
                LOGGER_CONFIG.ACTIVATE && jsLogger("[LOCK RELEASE] -", logName)
                pyodideLocked = false
            }
            return ret
        }
        return wrapper
    }
})()



/**Allow to delay the executions of various functions, until the pyodide environment
 * is ready.
 *
 * NOTES:
 *    1. DO NOT use this with subscribeWhenReady, which is expecting a sync callback.
 *    2. WARNING: this tool does NOT hold the async Lock logistic, so use it only in
 *       methods or functions that will themselves call other functions or methods
 *       that are actually locked (otherwise, deadlock!).
 * */
export const waitForPyodideReady = async()=>{
    LOGGER_CONFIG.ACTIVATE && jsLogger("[Wait4Pyodide] - ...")

    const maxWaitingTime = 20  // in seconds
    const attempts = 80
    const step_ms = Math.round(1000 * maxWaitingTime / attempts)

    let counter = 0
    while(!CONFIG.pyodideIsReady){
        await sleep(step_ms);
        if(++counter == attempts){
            throw new Error(`Couldn't access to pyodide environment in time (${maxWaitingTime}s)`)
        }
        LOGGER_CONFIG.ACTIVATE && jsLogger("[Wait4Pyodide] -", counter,'/',attempts, "attempts")
    }
}




/**Auto-subscription routine to document changes.
 * If the subscription is not possible yet (readyForSubscription[waitOn] is falsy), try again
 * @delay later until it works.
 *
 * @waitId :  Property to observe in readyForSubscription global object.Also used as subscription
 *            identifier.
 * @callback: Routine to run when the document changes
 * @options : An object with optional fields:
 *      .delay (=50): Time interval (in ms) to wait in between two subscription attempts.
 *      .now (=false): If true, ignore the CONFIG.subscriptionReady property and subscribe at call
 *              time. If false, a callback will be returned by the `subscribeWhenReady` function,
 *              that the caller can use to signal when the subscription is ready.
 *      .waitFor (=null): If given, it must be a boolean provider or a jquery identifier string,
 *              which will result in a function checking for the existence of that element in
 *              the DOM. This function will be called every .delay ms and the subscription will
 *              be delayed until it returns true. This has precedence over the .now option.
 *      .runOnly: if truthy, run the callback when ready, but do not subscribe to document changes.
 *      .maxTries: if not given 20 tries allowed.
 *
 * @throws: Error if maxTries subscriptions attempts are done without success.
 * */
export function subscribeWhenReady(waitId, callback, options={}){
    LOGGER_CONFIG.ACTIVATE && jsLogger('[Subscribing] - Enter', waitId)

    if(waitId in CONFIG.subscriptionReady){
        throw new Error(`Cannot subscribe several times to "${ waitId }".`)
    }

    let {now, delay, waitFor, runOnly, maxTries} = {
        delay: 50,
        now: false,
        waitFor: null,  // or string or boolean provider
        runOnly: false,
        maxTries: 20,
        ...options
    }
    now = now && !waitFor                   // Has to wait if waitFor is used (... XD )
    CONFIG.subscriptionReady[waitId] = now

    const waitForProp = typeof (waitFor)=='string'
    const checkReady  = !waitFor    ? ()=>null
                      : waitForProp ? ()=>{ CONFIG.subscriptionReady[waitId] = $(waitFor).length > 0 }
                                    : ()=>{ CONFIG.subscriptionReady[waitId] = waitFor() }

    const isNotReady =()=>{
        checkReady()
        return !( CONFIG.subscriptionReady[waitId] && globalThis.document$ )
    }


    const intervalId = setInterval(function(){
        if(isNotReady()){
            const nTries = CONFIG.subscriptionsTries[waitId]+1 || 1
            CONFIG.subscriptionsTries[waitId] = nTries
            if(nTries > maxTries){
                clearInterval(intervalId)
                throw new Error(`Impossible to subscribe to ${ waitId } in time: too many tries.`)
            }

        }else{
            clearInterval(intervalId)
            LOGGER_CONFIG.ACTIVATE && jsLogger('[Subscribing] -', waitId)
            const wrapper=function(){
                try{
                    callback()
                }catch(e){
                    console.error(e)
                }
            }
            if(runOnly){
                wrapper()
            }else{
                const subscript = document$.subscribe(wrapper)
                document.addEventListener(CONFIG.onDoneEvent, function(){
                    LOGGER_CONFIG.ACTIVATE && jsLogger('[Unsubscribing] -', waitId)
                    subscript.unsubscribe()
                })
            }
        }
    })

    if(!now){
        return ()=>{ CONFIG.subscriptionReady[waitId]=true }
    }
}
// TOKEN: end subscribeWhenReady








/**Flag to allow only one call to waitForClassesPoolReady.
 * */
let classesPoolSubscriptionDone = false


/**Routine to call unconditionally from overlord.js. It is used to make sure all the classes
 * required in the page are actually defined before trying to define the related instances
 * from the DOM content (this has become useful once the JS layer has been moved to JS
 * modules, which are async loaded).
 *
 * Passing in a callback also provides a way for a user customizing the theme to inject their
 * own logic/custom classes in CONFIG.CLASSES_POOL by overriding the call in overlord.js.
 * This way:
 *   - Their callback is called only after all the original classes have been defined.
 *   - The subscriptions are delayed until their callback returns a truthy value.
 *
 * @throws: Error if `applyWhenPoolReady` is given and it returns `undefined`
 *          (to prevent infinite loop).
 * */
export function waitForClassesPoolReady(applyWhenPoolReady=null){

  if(classesPoolSubscriptionDone){
    throw new Error("Cannot call several times waitForClassesPoolReady")
  }
  classesPoolSubscriptionDone = true

  const waitFor=()=>{
    // As long as class names remain in CONFIG.overlordClasses, those are not yet registered:
    if(CONFIG.overlordClasses.length){
      CONFIG.overlordClasses = CONFIG.overlordClasses.filter(
        className => !CONFIG.CLASSES_POOL[className]
      )
    }
    // Separated `if`, to gain 1 async cycle:
    if(!CONFIG.overlordClasses.length){
      CONFIG.overlordIsReady = !applyWhenPoolReady || applyWhenPoolReady()
      if(CONFIG.overlordIsReady === undefined){
        throw new Error(
          "`applyWhenPoolReady()` returned undefined: it has to return something."
        )
      }
    }
    return Boolean(CONFIG.overlordIsReady)
  }

  const maxTries = 600    // 600 * 50 ms = 30s
  subscribeWhenReady('Overlord', ()=>null, {waitFor, maxTries, runOnly: true})
}




/**To access CONFIG data from pyodide (mermaid, cutFeedback, ...).
 * */
export function config(){ return CONFIG }







/**Square brackets in "rich text format" must be escaped, otherwise they are messing up the
 * terminal formatting informations.
 * */
export const escapeSquareBrackets=msg=>{
    return msg.replace(CONFIG.ESCAPE_SQ_B, m=>SqBs[m])
}

export const unEscapeSquaredBrackets=msg=>{
    return msg.replace(CONFIG.UNESCAPE_SQ_B, m=>SqBs[m]||m)     // Why ||m ??
}

export function toSnake(msg){
    return msg.replace(/[A-Z]/g, m=>'_'+m.toLowerCase())
}

/**Ensure the given python code can safely be inserted into a JS template.
 * */
export function escapePyodideCodeForJsTemplates(code){
    return code.replace(/\\/g, '\\\\').replace(/"/g, '\\"')
}


/**Extract full information when something gets VERY wrong... */
export function youAreInTroubles(err, isError=false){
    if(isError) err = String(err).trimEnd()
    return `${ err }\n\n${ err.stack || '[no stack]' }\n${ CONFIG.MSG.bigFail }`
}


/**Takes a string and cut the "middle chunk" of them if it is considered too long (length > 1750),
 * shortening it in the following way:
 *   - keep the 500 first and 300 last chars
 *   - replace the middle with a message
 * */
export function textShortener(text){
    if(CONFIG.cutFeedback && text.length > CONFIG.feedbackShortener.limit){
        const head = text.slice(0,CONFIG.feedbackShortener.head)
        const tail = text.slice(-CONFIG.feedbackShortener.tail)
        text = `${ head }\n...\n${ CONFIG.feedbackShortener.msg }\n...\n${ tail }`
    }
    return text
}



/**Formatting function factory, for messages used in the jquery terminal.
 *
 * WARNING: the input message will be "escapeSquareBrackets"-ed.
 * */
const _richTextFormat = (content, style, color="", background="")=>{
    content = escapeSquareBrackets(content)
    return `[[${ style };${ color };${ background }]${ content }]`;
}

export const txtFormat = {
    error:   (content) => _richTextFormat(content, "b", "red"),
    warning: (content) => _richTextFormat(content, "ib", "orange"),
    info:    (content) => _richTextFormat(content, "i", "grey"),
    italic:  (content) => _richTextFormat(content, "i"),
    stress:  (content) => _richTextFormat(content, "b"),
    success: (content) => _richTextFormat(content, "ib", "green"),
    none:    escapeSquareBrackets,  // To override the defaults, if needed (see post processing)
}











/**NO_HTML and ALPHA (TOME_BASE in the python source) constants automatically transferred
 * from python during dev_ops/mkdocs_hooks operations.
 *
 * ****************************
 * * !!! DO NOT EDIT HERE !!! *
 * ****************************
 * */
const NO_HTML = '\'"&#><\n\t\r\\'
const ALPHA = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!#$%()*+,-./:;=?@^_`{|}~ "
const TOME_B = [...ALPHA].reduce((o,c,i)=>(o[c]=i,o), {})


const unBase =s=> [...s].reduce((v,c)=>v*ALPHA.length + TOME_B[c], 0)


/**@txt: CONFIG.LZW separated lines, with:
 *      1. A dot + dots separated unicode codePoints
 *      2. regular alpha
 *      3. compressed data, size 2
 *      4. ..., size 3,
 *      5. ...
 *
 * The compressed text always has one leading and one trailing dot:
 *      1. they allow to trim safely the encoded content, without any risk to trim spaces from
 *         the encoding alphabet.
 *      2. The leading dot allows to disambiguate the "big" section content of the alphabet,
 *         when no emojis are used in the original content.
 * */
export const decompressLZW=(compressed, compressOptionSrc)=>{

    // console.log(JSON.stringify(compressed))

    const [bigs, smalls, ...chunks] = compressed.trim().slice(0,-1).split(CONFIG.LZW)
    const tome = [
        [...NO_HTML],
        bigs=='.' ? [] : bigs.slice(1)
                             .split('.')
                             .map(n=>String.fromCodePoint(+n)),
        [...smalls],
    ].flat()

    let txt=[], size=1, out=[]
    chunks.forEach(chunk=>{
        size++
        if(chunk.length%size){
            throw new Error(
                `Wrong chunk during decompression: size=${size}, length=${chunk.length}.\n` +
                `You can deactivate the compression by using setting the pyodide_macros plugin ` +
                `option ${ compressOptionSrc } to false, until the theme gets fixed.`
            )
        }
        for(let i=0 ; i<chunk.length ; i+=size){
            txt.push(unBase(chunk.slice(i,i+size)))
        }
    })
    txt.forEach((iBase,i)=>{
        const s = tome[iBase]
        const fresh = s + (tome[txt[i+1]] || s)[0]
        out.push(s)
        tome.push(fresh)
    })
    return out.join('')
}


/**Decompress PAGE_IDES_CONFIG content if not already done.
 * */
export function decompressPagesIfNeeded(){
    if(typeof(PAGE_IDES_CONFIG)!='string') return;

    LOGGER_CONFIG.ACTIVATE && jsLogger('[CheckPoint] - decompress page LZW')
    globalThis.PAGE_IDES_CONFIG = decompressAndConvert(PAGE_IDES_CONFIG)
}


/**Decompress LZW encoded string to a JSON object.
 * */
export function decompressAndConvert(compressed){
    const decompressed = decompressLZW(compressed, "build.encrypted_js_data")
    const outcome      = JSON.parse(
        decompressed, (key,val)=>key=='attempts_left' && val=="Infinity" ? Infinity : val
    )
    return outcome
}









/**Create a button with tooltip, just like the python _html_builder one.
 * */
export function buttonWithTooltip(options, content){
    options = {
        buttonId: "",
        shift: 50,          // %
        fontSize: 1.5,      // em
        tipWidth: 15,       // em
        tipText: "",
        extraStyle: "",
        btnClass: "header-btn",
        ...options
    }
    options.tipWidth = options.tipWidth>0 ? `style="width:${ options.tipWidth }em;"` : ""
    const buttonId = !options.buttonId ? "" : `id="${ options.buttonId }" `
    return `
<button ${ buttonId }class="tooltip ${ options.btnClass }" type="button"
 style="--tool_shift:${ options.shift }%; font-size:${ options.fontSize }em;${ options.extraStyle }">
    <span class="tooltiptext bottom" ${ options.tipWidth }>${ options.tipText }</span>
    ${ content }
</button>
`
}



export const makeIdeJqButton = (kind, options) => {
    const button = `<img src="${ CONFIG.buttonIconsDirectory }/icons8-${ kind }-64.png" />`
    return $(buttonWithTooltip({shift:95, fontSize:1.1, ...options}, button))
}






const defaultOptions=(options, prop)=>({
    tagClass: "vertical",
    tagId: prop,
    extraStyles: "",    // For the outer element/tag

    label: prop,
    labelFirst: true,
    noLabel: false,

    inputId: prop+'-input',
    inputClass: "",

    tooltip: "",
    shift: 50,          // %
    tipWidth: 0,        // em ; 0 => auto
    tipClass: '',

    ...options
})


const stuffWithTooltip=(tag, options, htmlStuff)=>{

    const classes = [options.tagClass]
    if(options.tooltip) classes.push("tooltip")

    const tagId    = !options.tagId    ? '':`id="${ options.tagId }"`
    const tagClass = !options.tagClass ? '':`class="${ classes.join(' ') }"`
    const tagStyle = !options.tooltip  ? '':`style="--tool_shift:${ options.shift }%;${options.extraStyles??""}"`

    const tipStyle = !options.tooltip || !options.tipWidth ? '' : `style="width:${ options.tipWidth }em"`
    const tipClass = ['tooltiptext', options.tipClass || 'bottom'].join(' ')
    const tipSpan  = !options.tooltip  ? '':`<span class="${ tipClass }" ${ tipStyle }>${ options.tooltip }</span>`

    const label    = `<label for="${ options.inputId }" style="align-self:center">${ options.label }</label>`

    return $([
        `<${tag} ${ tagId }${ tagClass }${ tagStyle }>`,
            tipSpan,
            options.labelFirst ? '' : htmlStuff,
            !options.noLabel   ? label : '',
            options.labelFirst ? htmlStuff : '',
        `</${tag}>`
    ].join(''))
}


const valueAssigner=(obj, prop, inputProp='value')=>function(){
    obj[prop] = this[inputProp]
    // console.log(JSON.stringify(obj[prop]))
}




export function buildJqTextArea(obj, prop, options={}){
    options = defaultOptions(options, prop)
    const kls     = `class="full-width ${ options.inputClass||"" }"`
    const content = obj[prop]??""
    const nLines  = content.split('\n').length
    const html    = stuffWithTooltip(
        options.tag ?? 'div', options,
       `<textarea id="${ options.inputId }"  ${kls} placeholder="${ options.placeholder??"" }">${ content }</textarea>`,
    )

    const txtArea = html.find('textarea')
    txtArea.css('overflow-y','auto')
    txtArea.attr('rows', nLines)
    if(options.resize) txtArea.css('resize', options.resize)
    txtArea.on('change', valueAssigner(obj, prop))

    return html
}



export function buildJqCheckBox(obj, prop, options={}){
    options.tagClass    = ("horizontal "+(options.tagClass??"")).trim()
    options.extraStyles = "grid-template-columns: max-content max-content;grid-gap:5px;"
    options.labelFirst ??= false
    options = defaultOptions(options, prop)
    const kls = options.inputClass ? `class="${ options.inputClass }"`:""
    const html = stuffWithTooltip(
        'div', options,
        `<input type="checkbox" id="${ options.inputId }" ${kls} ${ obj[prop]?'checked':'' }>`,
    )
    return $(html).on('click', 'input', valueAssigner(obj, prop, 'checked'))
}



export function buildJqText(obj, prop, options={}){
    options = defaultOptions(options, prop)
    const kls  = options.inputClass ? `class="${ options.inputClass }"`:""
    const html = stuffWithTooltip(
        'div', options,
        `<input type="text" id="${ options.inputId }" ${kls} value="${ obj[prop]??"" }" placeholder="${ options.placeholder??"" }">`
    )
    return $(html).on('change', 'input', valueAssigner(obj, prop))
}



export function buildJqSelect(obj, prop, valuesArr, options={}){
    options = defaultOptions(options, prop)

    const kls    = options.inputClass ? `class="${ options.inputClass }"`:""
    const select = `<select id="${ options.inputId }" ${kls}>`+valuesArr.map( v=>
        `<option value="${ v }"${ v!==obj[prop]?'' : ' selected="selected"' }>${ v }</option>`
    ).join('')+"</select>"

    const html = stuffWithTooltip('div', options, select)
    return html.on('change', 'select', valueAssigner(obj, prop))
}











/**Apply a "download" action, given the content, name and type of the file to download.
 * See https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
 * about MIME types.
 * */
export function downloader(content, filename, mimeType="text/plain") {
    const blob = new Blob([content], {type: mimeType})
    const link = document.createElement("a")
    link.href = URL.createObjectURL(blob)
    link.download = filename
    link.click()
    URL.revokeObjectURL(link.href)
    link.remove()
}



/**Routine reusing the very same input[type=file] element (hidden in <head>) to upload content.
 * It must receive a callback that will handle the action to do with the content of the uploaded
 * file.
 * Returns a curried event executor: (cbk)=>(event executor function)
 * */
export var [uploader, uploaderAsync] = (function(){

    // https://developer.mozilla.org/en-US/docs/Web/API/File_API/Using_files_from_web_applications#example_showing_thumbnails_of_user-selected_images

    let jInput         = null
    let readMethod     = null   // readAsText / readAsDataURL / readAsArrayBuffer / readAsBinaryString
    let contentHandler = null   // Replaced on the fly at runtime
    let errorHandler   = null   // first error thrown during the reading process

    const inputId      = 'pyodide-file-uploader'
    const resumeHandler=_=>{ contentHandler = null }

    ;(_=>{
        // Defined in an isolated scope, to avoid the mistaken use of stuff defined here...
        jInput = $(`<input id="${ inputId }" name="file-uploader" type="file">`)
        $(document.head).append(jInput)

        jInput.on("cancel", resumeHandler)
        jInput[0].addEventListener(         // Doesn't wanna work through jQuery...
            "change",
            function(changeEvent){
                let iFile=1
                for(const file of changeEvent.target.files){

                    const reader  = new FileReader();
                    const isLast  = changeEvent.target.files.length==iFile++

                    reader.onabort = function(event){
                        resumeHandler()
                        throw errorHandler
                    }
                    reader.onload = function(event){
                        try{
                            contentHandler(event.target.result, file.name, isLast)
                        }catch(e){
                            errorHandler ||= e
                            reader.abort()
                        }
                        if(isLast) resumeHandler()      // to spot end of execution in async way
                    }
                    reader[readMethod](file)
                }
            },
            false
        )
    })()


    /**The showPicker method will raise an error, so possible to warn the user about what to do.
     * But it's not compatible with all browsers, so keep the orignal click logic anyway...
     * (but users wont' get any info about what's going wrong, in that case)
     * */
    const triggerInputFile=_=>{
        if(!jInput[0].showPicker){
            jInput[0].click()           // This is actually "async" (event!)
            return
        }
        try{
            jInput[0].showPicker()      // This is actually "async" (event!)
        }catch(e){
            // NOTE: Only the showPicker error should ever go there. Other errors aren't thrown
            //       in the same context...
            resumeHandler()     // Ensure release of the terminal, if async call
            if(!e.toString().includes('HTMLInputElement.showPicker')) throw e
            window.alert(CONFIG.lang.pickerFailure.msg)
        }
    }

    const uploader = (cbk, readAs='readAsText', multi=false)=>{
        contentHandler = cbk
        readMethod     = readAs
        jInput.prop('multiple', multi)
        triggerInputFile()
    }

    const uploaderAsync = async (...args)=>{
        errorHandler = null
        uploader(...args)
        // Wait until the upload is done, so that the uploaded content is usable during current run
        while(contentHandler){
            await sleep(200)
        }
        if(errorHandler){
            throw errorHandler  // propagate the error logic to the pyodide runtime environment
        }
    }

    return [uploader, uploaderAsync]
})()








/**Special JS Error: methods calls exclusions are tested from the JS runtime, instead of pyodide.
 * So, JS has to throw a special error that will mimic ("enough"...) the pattern of pyodide errors
 * and hance, will be considered legit errors.
 */
export class PythonError extends Error {
    toString() { return "Python" + super.toString() }
}


/**Note: the behavior of this in pyodide is a bit weird: because defined as a const, it is not
 * visible in pyodide from a terminal because it stays "hidden" even after assigning it to
 * getStorage/setStorage...
 * */
export const noStorage = function () {
    throw new PythonError(
        `Cannot read localStorage: no data available (looks like executions are stopped already).`
    )
}





/**Forbid writing these properties from pyodide.
 * */
export const PMT_LOCAL_STORAGE_KEYS_WRITE = Object.freeze(`
    code
    done
    hash
    name
    zip
`.trim().split(/\s+/))



/**Extract the given ID data from the localStorage, checking if it's not an outdated
 * or invalid structure.
 * @returns: [storage_data, upToDate]
 *
 * WARNING:
 *  1) Redactors might store extra fields in the LocalStorage, so DO NOT cleanup the thing...
 *  2) used in CodEx...
 * */
export function getIdeDataFromStorage(editorId, ide=null){

    // Originally, the storage value was just the user's code, so keep extracting as this:
    let codeOrStorageAsStr = localStorage.getItem(editorId) || ""

    let obj  = {}
    let code = codeOrStorageAsStr
    try{
      obj = JSON.parse(codeOrStorageAsStr || "{}")
      code = obj.code ?? ""
    }catch(_){}

    const upToDate = PMT_LOCAL_STORAGE_KEYS_WRITE.every(k=> k in obj)
    const storage  = upToDate ? obj : freshStore(code, obj, ide)

    return [storage, upToDate]
}



/**Build a default IDE storage object, taking care of the logic involved in various PMT versions.
 *
 * WARNING: Redactors might store extra fields in the LocalStorage, so DO NOT cleanup the thing...
 * */
export function freshStore(code, storage={}, ide=null){

    storage.code = code || ""
    storage.done ??= 0              // -1: fail, 0: unknown, 1:success
    if(ide) ide.forceUpdateStorage(storage)
    return storage
}









// For backward compatibility (hooks and co'):
globalThis.PythonError        = PythonError
globalThis.CONFIG             = CONFIG
globalThis.subscribeWhenReady = subscribeWhenReady
LOGGER_CONFIG.ACTIVATE && console.log("async subscriber updated")

// Access from pyodide + IdeZipManager logistic + backward compatibility:
globalThis.getStorage    = noStorage
globalThis.setStorage    = noStorage
globalThis.delStorage    = noStorage
globalThis.keysStorage   = noStorage
globalThis.config        = config
globalThis.downloader    = downloader
globalThis.uploader      = uploader
globalThis.uploaderAsync = uploaderAsync
