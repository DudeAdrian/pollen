/**
 * Pollen Python Agent - TypeScript Bridge
 * 
 * This module provides integration between the TypeScript Pollen ecosystem
 * and the Python comprehensive AI agent (port 9000).
 * 
 * The Python agent provides:
 * - Advanced LLM integration (Ollama)
 * - Content generation (websites, apps, media)
 * - Social media automation
 * - Wellness protocol execution
 * - Shadow accumulation & graduation
 * 
 * @module pollen-python
 */

export interface PythonAgentConfig {
  host: string;
  port: number;
  enabled: boolean;
}

export interface PythonAgentStatus {
  running: boolean;
  agentId?: string;
  hiveConnected: boolean;
  shadowBalance: number;
  pendingTasks: number;
}

/**
 * Python Agent Client
 * Communicates with the Python FastAPI server
 */
export class PythonAgentClient {
  private baseUrl: string;

  constructor(config: PythonAgentConfig) {
    this.baseUrl = `http://${config.host}:${config.port}`;
  }

  async getStatus(): Promise<PythonAgentStatus> {
    const response = await fetch(`${this.baseUrl}/status`);
    return response.json();
  }

  async spawn(agentName: string): Promise<{ agentId: string; success: boolean }> {
    const response = await fetch(`${this.baseUrl}/spawn`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent_name: agentName }),
    });
    return response.json();
  }

  async executeTask(taskType: string, payload: Record<string, unknown>): Promise<unknown> {
    const response = await fetch(`${this.baseUrl}/task/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ task_type: taskType, payload }),
    });
    return response.json();
  }

  async createContent(
    contentType: string,
    prompt: string,
    options?: Record<string, unknown>
  ): Promise<unknown> {
    const response = await fetch(`${this.baseUrl}/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content_type: contentType, prompt, options }),
    });
    return response.json();
  }

  async getWellnessStatus(): Promise<unknown> {
    const response = await fetch(`${this.baseUrl}/wellness/status`);
    return response.json();
  }

  async submitProof(
    activityType: string,
    proofHash: string,
    valueScore: number
  ): Promise<unknown> {
    const response = await fetch(`${this.baseUrl}/consensus/proof`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ activity_type: activityType, proof_hash: proofHash, value_score: valueScore }),
    });
    return response.json();
  }
}

export const defaultConfig: PythonAgentConfig = {
  host: 'localhost',
  port: 9000,
  enabled: true,
};
