# Production Backup Manifest

This commit is a recovery snapshot of the verified working PUSULA production deployment.

- Snapshot date: 2026-09-13
- Vercel project: `pusula-nsosyal-ui-v3`
- Vercel project ID: `prj_LNNe7Y60gNsOrPl0agatqwkRo0o2`
- Production deployment ID: `dpl_AFKijVadXC5PiK6oXY7kXJgSudki`
- Immutable deployment URL: `https://pusula-nsosyal-ui-v3-2gmgagp5x-ecemboz123456-4318s-projects.vercel.app`
- Public alias: `https://pusula-nsosyal-ui-v3.vercel.app/`

## Included runtime/source files

- `index.html`
- `client.js`
- `polish.js`
- `polish.core-06a9d80c.js`
- `polish.css`
- `polish.core-10bc39ea.css`
- `lucide.min.js`
- `api/pusula.js`
- `vercel.json`
- `SHA256SUMS.txt`

## Verification performed before commit

- All production runtime assets were downloaded directly from the immutable Vercel deployment URL.
- Runtime references are local to the same project: `/client.js`, `/polish.js`, `/polish.css`, `/lucide.min.js`, and local `polish.core-*` assets.
- `client.js` calls only the same-origin `/api/pusula` endpoint.
- No dependency on the deleted `pusula-nsosyal-demo` project or the old helper/test Vercel projects is permitted by the snapshot verification step.
- JavaScript source syntax checks must pass before this snapshot can be committed.
- Secrets, `.env*`, and local `.vercel/` state are intentionally excluded.

## External data dependency

The API intentionally reads the PUSULA dataset from `asimonmsz-design/pusula` at `kod/veri/etiketli_havuz.json`. That is application data, not a Vercel project dependency.

## Recovery rule

Treat this commit as a known-good source snapshot. Restore to a preview deployment first and verify visually/API-wise before replacing production. Do not connect this backup repository to automatic production deployment unless explicitly intended.
