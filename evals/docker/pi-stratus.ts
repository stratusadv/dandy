import type { ExtensionAPI } from '@mariozechner/pi-coding-agent'

export default function (pi: ExtensionAPI) {
  pi.registerProvider('stratus', {
    name: 'Stratus',
    baseUrl: `${process.env.AI_API_HOST}:443/v1`,
    apiKey: process.env.AI_API_KEY,
    api: 'openai-completions',
    models: [
      {
        id: 'stratus.turbo',
        name: 'Turbo',
        reasoning: false,
        input: ['text'],
        cost: { input: 1.0, output: 5.0, cacheRead: 0, cacheWrite: 0 },
        contextWindow: 48000,
        maxTokens: 16000,
      },
    ],
  })
}
