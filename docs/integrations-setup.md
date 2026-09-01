# إعداد SAP وLLM

## SAP

`src/integrations/sap_adapter.py` يستخدم SAP OData عبر OAuth2 `client_credentials` عند تفعيل الربط الحقيقي. يجب إعداد `SAP_HOST` و`SAP_TOKEN_URL` و`SAP_CLIENT_ID` و`SAP_CLIENT_SECRET` و`SAP_ALLOWED_HOSTS`. يُشترط HTTPS وallowlist للنطاق، ويظل `SAP_READ_ONLY=true` و`SAP_DRY_RUN=true` افتراضيًا. لا يُقبل Basic Auth في هذا المسار، ولا تدعم الواجهة عمليات الكتابة.

## LLM

`src/ai/llm_provider.py` يختار المزود من `DEFAULT_AI_PROVIDER` ويستخدم مفاتيح الخادم مثل `OPENAI_API_KEY` و`ANTHROPIC_API_KEY` و`GOOGLE_API_KEY` و`DEEPSEEK_API_KEY`. المفاتيح لا تُرسل إلى الواجهة ولا تُسجّل. يُفضّل `FALLBACK_PROVIDER=local` للبيانات الحساسة، مع حدود تكلفة يومية وشهرية، وتُستبعد المزودات غير المهيأة تلقائيًا.

## البيئة

انسخ `.env.example` إلى `.env` محليًا فقط، ثم استبدل القيم التي تبدأ بـ `replace-with-` بقيم محلية أو من مدير أسرار. لا يوجد ملف `.env` مملوء داخل الأرشيف لأن إدراج أسرار فعلية في مشروع أو ZIP يعتبر تسريبًا. يمكن إنشاء ملف تطوير عشوائيًا عبر:

```bash
python3 tools/init-env.py
```

بعد التهيئة، افحص `git status` وتأكد أن `.env` مستبعد من Git، وأن الإنتاج يستخدم Secret Manager وTLS وrotation وleast privilege.
