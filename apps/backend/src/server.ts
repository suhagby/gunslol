import Fastify from 'fastify';
import cors from '@fastify/cors';
import { registerLinkRoutes } from './routes/links';

const server = Fastify();

server.register(cors);

registerLinkRoutes(server);

export async function start() {
  try {
    await server.listen({ port: 3001, host: '0.0.0.0' });
    console.log('Backend running on http://localhost:3001');
  } catch (err) {
    server.log.error(err);
    process.exit(1);
  }
}

if (require.main === module) {
  start();
}
