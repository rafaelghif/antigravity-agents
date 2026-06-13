const fs = require('fs');
const path = require('path');

const openapiPath = process.argv[2];
const outputPath = process.argv[3];

if (!openapiPath || !outputPath) {
  console.error("Usage: node generate-client.js <openapi.json> <output.ts>");
  process.exit(1);
}

if (!fs.existsSync(openapiPath)) {
  console.error(`Error: openapi file not found at ${openapiPath}`);
  process.exit(1);
}

const schema = JSON.parse(fs.readFileSync(openapiPath, 'utf8'));
let code = `/**
 * Auto-generated API client by Antigravity Agent Core.
 * DO NOT EDIT DIRECTLY.
 */

`;

const baseUrl = schema.servers && schema.servers[0] ? schema.servers[0].url : '/';

function mapType(prop) {
  if (!prop) return 'any';
  if (prop.$ref) {
    return prop.$ref.split('/').pop();
  }
  if (prop.type === 'array') {
    return `${mapType(prop.items)}[]`;
  }
  if (prop.type === 'string') return 'string';
  if (prop.type === 'integer' || prop.type === 'number') return 'number';
  if (prop.type === 'boolean') return 'boolean';
  if (prop.type === 'object') {
    if (prop.properties) {
      let sub = '{ ';
      for (const [k, v] of Object.entries(prop.properties)) {
        const req = prop.required && prop.required.includes(k) ? '' : '?';
        sub += `${k}${req}: ${mapType(v)}; `;
      }
      sub += '}';
      return sub;
    }
    return 'Record<string, any>';
  }
  return 'any';
}

if (schema.components && schema.components.schemas) {
  for (const [name, definition] of Object.entries(schema.components.schemas)) {
    code += `export interface ${name} {\n`;
    if (definition.properties) {
      for (const [propName, propDef] of Object.entries(definition.properties)) {
        const required = definition.required && definition.required.includes(propName) ? '' : '?';
        code += `  ${propName}${required}: ${mapType(propDef)};\n`;
      }
    }
    code += `}\n\n`;
  }
}

code += `export class APIClient {\n`;
code += `  private baseUrl: string;\n`;
code += `  private headers: Record<string, string>;\n\n`;
code += `  constructor(baseUrl: string = '${baseUrl}', headers: Record<string, string> = {}) {\n`;
code += `    this.baseUrl = baseUrl.replace(/\\/$/, '');\n`;
code += `    this.headers = {\n`;
code += `      'Content-Type': 'application/json',\n`;
code += `      ...headers\n`;
code += `    };\n`;
code += `  }\n\n`;
code += `  setToken(token: string) {\n`;
code += `    this.headers['Authorization'] = \`Bearer \${token}\`;\n`;
code += `  }\n\n`;

if (schema.paths) {
  for (const [pathStr, pathObj] of Object.entries(schema.paths)) {
    for (const [method, operation] of Object.entries(pathObj)) {
      if (!['get', 'post', 'put', 'delete', 'patch'].includes(method.toLowerCase())) continue;
      
      const operationId = operation.operationId || `${method}${pathStr.replace(/[^a-zA-Z0-9]/g, '_')}`;
      const cleanMethodName = operationId
        .replace(/_([a-z])/g, (g) => g[1].toUpperCase())
        .replace(/[^a-zA-Z0-9]/g, '')
        .replace(/^[A-Z]/, (c) => c.toLowerCase());
      
      const parameters = operation.parameters || [];
      const pathParams = parameters.filter(p => p.in === 'path');
      const queryParams = parameters.filter(p => p.in === 'query');
      
      let methodArgs = [];
      let pathInterpolation = pathStr;
      
      for (const p of pathParams) {
        methodArgs.push(`${p.name}: ${mapType(p)}`);
        pathInterpolation = pathInterpolation.replace(`{${p.name}}`, `\${${p.name}}`);
      }
      
      let hasBody = false;
      let bodyType = 'any';
      if (operation.requestBody) {
        hasBody = true;
        const content = operation.requestBody.content;
        if (content && content['application/json'] && content['application/json'].schema) {
          bodyType = mapType(content['application/json'].schema);
        }
        methodArgs.push(`body: ${bodyType}`);
      }
      
      let hasQuery = queryParams.length > 0;
      if (hasQuery) {
        let qType = '{ ';
        for (const q of queryParams) {
          const req = q.required ? '' : '?';
          qType += `${q.name}${req}: ${mapType(q)}; `;
        }
        qType += '}';
        methodArgs.push(`query?: ${qType}`);
      }
      
      let responseType = 'any';
      if (operation.responses && operation.responses['200'] && operation.responses['200'].content) {
        const content = operation.responses['200'].content;
        if (content['application/json'] && content['application/json'].schema) {
          responseType = mapType(content['application/json'].schema);
        }
      } else if (operation.responses && operation.responses['201'] && operation.responses['201'].content) {
        const content = operation.responses['201'].content;
        if (content['application/json'] && content['application/json'].schema) {
          responseType = mapType(content['application/json'].schema);
        }
      }

      code += `  async ${cleanMethodName}(${methodArgs.join(', ')}): Promise<${responseType}> {\n`;
      
      if (hasQuery) {
        code += `    const queryParams = new URLSearchParams();\n`;
        code += `    if (query) {\n`;
        code += `      for (const [key, value] of Object.entries(query)) {\n`;
        code += `        if (value !== undefined && value !== null) {\n`;
        code += `          queryParams.append(key, String(value));\n`;
        code += `        }\n`;
        code += `      }\n`;
        code += `    }\n`;
        code += `    const queryString = queryParams.toString() ? \`?\${queryParams.toString()}\` : '';\n`;
      } else {
        code += `    const queryString = '';\n`;
      }
      
      code += `    const url = \`\${this.baseUrl}${pathInterpolation}\${queryString}\`;\n`;
      
      code += `    const options: RequestInit = {\n`;
      code += `      method: '${method.toUpperCase()}',\n`;
      code += `      headers: this.headers,\n`;
      if (hasBody) {
        code += `      body: JSON.stringify(body),\n`;
      }
      code += `    };\n\n`;
      
      code += `    const response = await fetch(url, options);\n`;
      code += `    if (!response.ok) {\n`;
      code += `      throw new Error(\`HTTP Error \${response.status}: \${response.statusText}\`);\n`;
      code += `    }\n`;
      code += `    return response.json();\n`;
      code += `  }\n\n`;
    }
  }
}

code += `}\n`;

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, code, 'utf8');
console.log(`Successfully generated API client with ${Object.keys(schema.components?.schemas || {}).length} types to ${outputPath}`);
