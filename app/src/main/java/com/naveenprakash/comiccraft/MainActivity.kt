package com.naveenprakash.comiccraft

import android.app.*
import android.content.*
import android.graphics.*
import android.graphics.drawable.ColorDrawable
import android.net.Uri
import android.os.*
import android.provider.MediaStore
import android.view.*
import android.widget.*
import org.json.JSONArray
import org.json.JSONObject
import java.io.*
import java.net.HttpURLConnection
import java.net.URL
import java.text.SimpleDateFormat
import java.util.*
import java.util.concurrent.Executors

data class Panel(
    val number: Int,
    val title: String,
    val scene: String,
    val imagePrompt: String,
    val caption: String,
    val narration: String,
    val dialogue: String,
    var bitmap: Bitmap? = null
)

class MainActivity : Activity() {
    private val executor = Executors.newSingleThreadExecutor()
    private lateinit var root: LinearLayout
    private lateinit var story: EditText
    private lateinit var character: EditText
    private lateinit var setting: EditText
    private lateinit var tone: Spinner
    private lateinit var art: Spinner
    private lateinit var geminiKey: EditText
    private lateinit var hfKey: EditText
    private lateinit var generate: Button
    private lateinit var progress: TextView
    private val panels = mutableListOf<Panel>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        showForm()
    }

    private fun showForm() {
        root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(18), dp(18), dp(18), dp(24))
            setBackgroundColor(Color.WHITE)
        }

        val scroll = ScrollView(this)
        scroll.addView(root)

        title("ComicCraft")
        subtitle("Turn one idea into a five-panel AI comic.")

        story = edit("Story Prompt", "A brave fox discovers a hidden doorway in an enchanted forest...", 5)
        character = edit("Main Character Name", "Arin")
        setting = edit("Setting", "Enchanted forest")

        tone = spinner("Story Tone", arrayOf("light-hearted", "dramatic", "poetic", "funny"))
        art = spinner("Art Style", arrayOf("comic book", "anime", "pixel art", "realistic"))

        subtitle("API keys")
        geminiKey = edit("Gemini API Key", "", 1, true)
        hfKey = edit("Hugging Face Token", "", 1, true)

        val savedGemini = getPreferences(0).getString("gemini", "") ?: ""
        val savedHf = getPreferences(0).getString("hf", "") ?: ""
        geminiKey.setText(savedGemini)
        hfKey.setText(savedHf)

        generate = Button(this).apply {
            text = "Generate My Comic"
            setTextColor(Color.WHITE)
            background = getDrawable(com.naveenprakash.comiccraft.R.drawable.button_bg)
            setPadding(dp(16), dp(12), dp(16), dp(12))
            setOnClickListener { startGeneration() }
        }
        root.addView(generate, lp(0, 54, 0, 18))

        progress = TextView(this).apply {
            textSize = 14f
            setTextColor(Color.DKGRAY)
        }
        root.addView(progress)

        setContentView(scroll)
    }

    private fun startGeneration() {
        val g = geminiKey.text.toString().trim()
        val h = hfKey.text.toString().trim()
        if (story.text.trim().length < 5 || character.text.trim().isEmpty() || setting.text.trim().isEmpty()) {
            toast("Please fill story, character and setting.")
            return
        }
        if (g.isEmpty()) {
            toast("Enter your Gemini API key.")
            return
        }
        if (h.isEmpty()) {
            toast("Enter your Hugging Face token.")
            return
        }

        getPreferences(0).edit().putString("gemini", g).putString("hf", h).apply()
        generate.isEnabled = false
        progress.text = "Creating outline with Gemini..."

        executor.execute {
            try {
                val outline = GeminiApi(g).outline(
                    story.text.toString(), character.text.toString(),
                    setting.text.toString(), tone.selectedItem.toString(),
                    art.selectedItem.toString()
                )
                runOnUiThread { progress.text = "Writing dialogue and narration..." }

                val scripts = GeminiApi(g).story(
                    story.text.toString(), character.text.toString(),
                    setting.text.toString(), tone.selectedItem.toString(),
                    art.selectedItem.toString(), outline.toString()
                )

                panels.clear()
                val outlineArr = outline.getJSONArray("panels")
                val storyArr = scripts.getJSONArray("panels")
                val storyMap = HashMap<Int, JSONObject>()
                for (i in 0 until storyArr.length()) {
                    val s = storyArr.getJSONObject(i)
                    storyMap[s.getInt("panel_number")] = s
                }

                for (i in 0 until outlineArr.length()) {
                    val o = outlineArr.getJSONObject(i)
                    val n = o.getInt("panel_number")
                    val s = storyMap[n] ?: JSONObject()
                    panels.add(
                        Panel(
                            n,
                            o.optString("title"),
                            o.optString("scene_description"),
                            o.optString("image_prompt"),
                            s.optString("caption"),
                            s.optString("narration"),
                            s.optString("dialogue")
                        )
                    )
                }

                val hf = HuggingFaceApi(h)
                for ((idx, p) in panels.withIndex()) {
                    val current = idx + 1
                    runOnUiThread { progress.text = "Generating illustration $current/5..." }
                    p.bitmap = hf.generate(p.imagePrompt, art.selectedItem.toString())
                }

                runOnUiThread {
                    generate.isEnabled = true
                    progress.text = "Comic ready."
                    showResult()
                }
            } catch (e: Exception) {
                runOnUiThread {
                    generate.isEnabled = true
                    progress.text = ""
                    toast(e.message ?: "Generation failed.")
                }
            }
        }
    }

    private fun showResult() {
        root.removeAllViews()
        title("Your Comic Is Ready")
        subtitle("${character.text} • ${setting.text} • ${tone.selectedItem} • ${art.selectedItem}")

        val pdfButton = Button(this).apply {
            text = "Export Comic as PDF"
            setTextColor(Color.WHITE)
            background = getDrawable(R.drawable.button_bg)
            setOnClickListener { exportPdf() }
        }
        root.addView(pdfButton, lp(0, 54, 0, 14))

        for (p in panels.sortedBy { it.number }) {
            val card = LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL
                setPadding(dp(12), dp(12), dp(12), dp(18))
            }
            val head = TextView(this).apply {
                text = "Panel ${p.number}: ${p.title}"
                textSize = 20f
                setTextColor(Color.rgb(30, 25, 35))
                setTypeface(typeface, Typeface.BOLD)
            }
            card.addView(head)
            p.bitmap?.let {
                val image = ImageView(this).apply {
                    setImageBitmap(it)
                    adjustViewBounds = true
                    scaleType = ImageView.ScaleType.CENTER_CROP
                }
                card.addView(image, lp(0, 280, 0, 10))
            }
            addText(card, p.scene)
            if (p.caption.isNotBlank()) addText(card, "Caption: ${p.caption}")
            if (p.narration.isNotBlank()) addText(card, "Narration: ${p.narration}")
            if (p.dialogue.isNotBlank()) addText(card, "Dialogue: “${p.dialogue}”")
            root.addView(card, lp(0, -2, 0, 8))
        }

        val again = Button(this).apply {
            text = "Create Another Comic"
            setOnClickListener { showForm() }
        }
        root.addView(again, lp(0, 54, 0, 20))
    }

    private fun exportPdf() {
        try {
            val fileName = "ComicCraft_" + SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(Date()) + ".pdf"
            val pdf = PdfDocument()
            val pageW = 595
            val pageH = 842

            for (p in panels) {
                val page = pdf.startPage(PdfDocument.PageInfo.Builder(pageW, pageH, p.number).create())
                val c = page.canvas
                val paint = Paint(Paint.ANTI_ALIAS_FLAG)
                paint.color = Color.BLACK
                paint.textSize = 18f
                paint.typeface = Typeface.DEFAULT_BOLD
                c.drawText("Panel ${p.number}: ${p.title}", 36f, 42f, paint)

                p.bitmap?.let { bmp ->
                    val maxW = 523f
                    val maxH = 350f
                    val scale = minOf(maxW / bmp.width, maxH / bmp.height)
                    val w = bmp.width * scale
                    val h = bmp.height * scale
                    val dst = RectF(36f, 60f, 36f + w, 60f + h)
                    c.drawBitmap(bmp, null, dst, paint)
                }

                paint.typeface = Typeface.DEFAULT
                paint.textSize = 11f
                var y = 435f
                y = drawWrapped(c, "Scene: ${p.scene}", 36f, y, 523f, paint)
                if (p.caption.isNotBlank()) y = drawWrapped(c, "Caption: ${p.caption}", 36f, y + 8, 523f, paint)
                if (p.narration.isNotBlank()) y = drawWrapped(c, "Narration: ${p.narration}", 36f, y + 8, 523f, paint)
                if (p.dialogue.isNotBlank()) drawWrapped(c, "Dialogue: ${p.dialogue}", 36f, y + 8, 523f, paint)

                pdf.finishPage(page)
            }

            val values = android.content.ContentValues().apply {
                put(MediaStore.Downloads.DISPLAY_NAME, fileName)
                put(MediaStore.Downloads.MIME_TYPE, "application/pdf")
                put(MediaStore.Downloads.RELATIVE_PATH, android.os.Environment.DIRECTORY_DOWNLOADS)
            }
            val uri = contentResolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values)
                ?: throw IOException("Could not create Downloads file.")
            contentResolver.openOutputStream(uri)?.use { pdf.writeTo(it) }
            pdf.close()
            toast("PDF saved to Downloads/$fileName")
        } catch (e: Exception) {
            toast("PDF export failed: ${e.message}")
        }
    }

    private fun drawWrapped(c: Canvas, text: String, x: Float, startY: Float, width: Float, paint: Paint): Float {
        val words = text.split(" ")
        var line = ""
        var y = startY
        for (word in words) {
            val test = if (line.isEmpty()) word else "$line $word"
            if (paint.measureText(test) > width) {
                c.drawText(line, x, y, paint)
                y += 16f
                line = word
            } else line = test
        }
        if (line.isNotEmpty()) {
            c.drawText(line, x, y, paint)
            y += 16f
        }
        return y
    }

    private fun addText(parent: LinearLayout, text: String) {
        val v = TextView(this).apply {
            this.text = text
            textSize = 14f
            setTextColor(Color.DKGRAY)
            setPadding(0, dp(5), 0, dp(5))
        }
        parent.addView(v)
    }

    private fun title(text: String) {
        root.addView(TextView(this).apply {
            this.text = text
            textSize = 32f
            setTextColor(Color.rgb(25, 20, 30))
            setTypeface(typeface, Typeface.BOLD)
            setPadding(0, 0, 0, dp(6))
        }, lp(0, -2, 0, 2))
    }

    private fun subtitle(text: String) {
        root.addView(TextView(this).apply {
            this.text = text
            textSize = 15f
            setTextColor(Color.GRAY)
            setPadding(0, 0, 0, dp(16))
        }, lp(0, -2, 0, 4))
    }

    private fun edit(label: String, hint: String, lines: Int = 1, password: Boolean = false): EditText {
        val box = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        val l = TextView(this).apply {
            text = label
            textSize = 14f
            setTypeface(typeface, Typeface.BOLD)
            setTextColor(Color.DKGRAY)
        }
        box.addView(l)
        val e = EditText(this).apply {
            this.hint = hint
            setTextSize(15f)
            setBackgroundResource(R.drawable.edit_bg)
            this.minLines = lines
            this.maxLines = maxOf(lines, 6)
            if (password) inputType = android.text.InputType.TYPE_CLASS_TEXT or android.text.InputType.TYPE_TEXT_VARIATION_PASSWORD
        }
        box.addView(e, lp(0, if (lines > 1) 120 else 52, 0, 8))
        root.addView(box)
        return e
    }

    private fun spinner(label: String, values: Array<String>): Spinner {
        val box = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        box.addView(TextView(this).apply {
            text = label
            textSize = 14f
            setTypeface(typeface, Typeface.BOLD)
            setTextColor(Color.DKGRAY)
        })
        val s = Spinner(this)
        s.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, values)
        box.addView(s, lp(0, 52, 0, 8))
        root.addView(box)
        return s
    }

    private fun lp(w: Int, h: Int, left: Int, bottom: Int): LinearLayout.LayoutParams {
        val p = LinearLayout.LayoutParams(if (w == 0) LinearLayout.LayoutParams.MATCH_PARENT else w, if (h < 0) LinearLayout.LayoutParams.WRAP_CONTENT else dp(h))
        p.setMargins(dp(left), 0, 0, dp(bottom))
        return p
    }

    private fun dp(v: Int) = (v * resources.displayMetrics.density).toInt()
    private fun toast(s: String) = runOnUiThread { Toast.makeText(this, s, Toast.LENGTH_LONG).show() }

    override fun onDestroy() {
        executor.shutdownNow()
        super.onDestroy()
    }
}

class GeminiApi(private val key: String) {
    private val model = "gemini-2.5-flash"

    fun outline(story: String, character: String, setting: String, tone: String, style: String): JSONObject {
        val prompt = """
Create a coherent 5-panel comic outline.
STORY: $story
MAIN CHARACTER: $character
SETTING: $setting
TONE: $tone
ART STYLE: $style
Return ONLY JSON with this exact shape:
{"panels":[{"panel_number":1,"title":"","scene_description":"","image_prompt":""}, ...]}
Exactly 5 panels. Keep the same protagonist, appearance, clothing and visual identity. Include beginning, escalation, turning point and satisfying ending. No readable text or watermark in artwork.
""".trimIndent()
        return JSONObject(call(prompt))
    }

    fun story(story: String, character: String, setting: String, tone: String, style: String, outline: String): JSONObject {
        val prompt = """
Create a complete 5-panel comic script.
STORY: $story
MAIN CHARACTER: $character
SETTING: $setting
TONE: $tone
ART STYLE: $style
OUTLINE: $outline
Return ONLY JSON:
{"panels":[{"panel_number":1,"caption":"","narration":"","dialogue":""}, ...]}
Exactly 5 panels. Keep continuity and concise text.
""".trimIndent()
        return JSONObject(call(prompt))
    }

    private fun call(prompt: String): String {
        val url = URL("https://generativelanguage.googleapis.com/v1beta/models/$model:generateContent?key=$key")
        val body = JSONObject()
            .put("contents", JSONArray().put(JSONObject().put("parts", JSONArray().put(JSONObject().put("text", prompt)))))
            .put("generationConfig", JSONObject().put("responseMimeType", "application/json"))
        val conn = url.openConnection() as HttpURLConnection
        conn.requestMethod = "POST"
        conn.connectTimeout = 30000
        conn.readTimeout = 180000
        conn.setRequestProperty("Content-Type", "application/json")
        conn.doOutput = true
        conn.outputStream.use { it.write(body.toString().toByteArray(Charsets.UTF_8)) }
        val code = conn.responseCode
        val stream = if (code in 200..299) conn.inputStream else conn.errorStream
        val response = stream.bufferedReader().use { it.readText() }
        if (code !in 200..299) throw IOException("Gemini HTTP $code: $response")
        val obj = JSONObject(response)
        val text = obj.getJSONArray("candidates").getJSONObject(0)
            .getJSONObject("content").getJSONArray("parts").getJSONObject(0).getString("text")
        return extractJson(text)
    }

    private fun extractJson(s: String): String {
        val start = s.indexOf('{')
        val end = s.lastIndexOf('}')
        if (start < 0 || end <= start) throw IOException("Gemini returned invalid JSON.")
        return s.substring(start, end + 1)
    }
}

class HuggingFaceApi(private val token: String) {
    private val model = "stabilityai/stable-diffusion-xl-base-1.0"

    fun generate(prompt: String, style: String): Bitmap {
        val enhanced = """
$prompt
High quality $style comic illustration. Consistent main character design, clothing and appearance. Strong facial expression, detailed environment, cinematic lighting, professional composition, clean artwork. No readable text, watermark or logo.
""".trimIndent()

        val url = URL("https://router.huggingface.co/hf-inference/models/$model")
        val conn = url.openConnection() as HttpURLConnection
        conn.requestMethod = "POST"
        conn.connectTimeout = 30000
        conn.readTimeout = 300000
        conn.setRequestProperty("Authorization", "Bearer $token")
        conn.setRequestProperty("Content-Type", "application/json")
        conn.doOutput = true
        val body = JSONObject().put("inputs", enhanced)
        conn.outputStream.use { it.write(body.toString().toByteArray(Charsets.UTF_8)) }
        val code = conn.responseCode
        if (code !in 200..299) {
            val err = conn.errorStream?.bufferedReader()?.use { it.readText() } ?: "unknown error"
            throw IOException("Hugging Face HTTP $code: $err")
        }
        return BitmapFactory.decodeStream(conn.inputStream) ?: throw IOException("HF returned no image.")
    }
}
