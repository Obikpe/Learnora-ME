import http from 'k6/http';
import { check, sleep } from 'k6';

const API_BASE_URL = (__ENV.API_BASE_URL || '').replace(/\/+$/, '');
if (!API_BASE_URL) {
  throw new Error('Set API_BASE_URL to the backend origin, for example https://your-staging-backend.example');
}

const host = API_BASE_URL.replace(/^https?:\/\//i, '').split('/')[0].split(':')[0].toLowerCase();
const isLoopback = host === 'localhost' || host === '127.0.0.1' || host === '::1';
const loadTestEnvironment = (__ENV.LOAD_TEST_ENV || 'staging').toLowerCase();

if (!isLoopback && __ENV.ALLOW_REMOTE_LOAD_TEST !== 'true') {
  throw new Error('Remote load testing is disabled. Set ALLOW_REMOTE_LOAD_TEST=true only for an approved non-production target.');
}
if (loadTestEnvironment === 'production' && __ENV.ALLOW_PRODUCTION_LOAD_TEST !== 'true') {
  throw new Error('Production load testing requires separate explicit approval via ALLOW_PRODUCTION_LOAD_TEST=true.');
}

const maxVUs = Number(__ENV.MAX_VUS || 100);
if (!Number.isInteger(maxVUs) || maxVUs < 1 || maxVUs > 1000) {
  throw new Error('MAX_VUS must be an integer between 1 and 1000.');
}

const rampTargets = [10, 50, 100, 250, 500, 1000].filter((target) => target <= maxVUs);
if (rampTargets.length === 0 || rampTargets[rampTargets.length - 1] !== maxVUs) {
  rampTargets.push(maxVUs);
}

const stages = [];
for (const target of rampTargets) {
  stages.push({ duration: '1m', target });
  stages.push({ duration: '2m', target });
}
stages.push({ duration: '1m', target: 0 });

export const options = {
  stages,
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<2000'],
    checks: ['rate>0.99'],
  },
  discardResponseBodies: false,
};

export default function () {
  const responses = http.batch([
    ['GET', `${API_BASE_URL}/api/public/courses`, null, {
      headers: { Accept: 'application/json' },
      timeout: '10s',
      tags: { endpoint: 'public-course-catalogue' },
    }],
    ['GET', `${API_BASE_URL}/api/public/tracks`, null, {
      headers: { Accept: 'application/json' },
      timeout: '10s',
      tags: { endpoint: 'public-track-catalogue' },
    }],
  ]);

  const [coursesResponse, tracksResponse] = responses;
  let coursesPayload = null;
  let tracksPayload = null;
  try { coursesPayload = coursesResponse.json(); } catch (_) { coursesPayload = null; }
  try { tracksPayload = tracksResponse.json(); } catch (_) { tracksPayload = null; }

  check(coursesResponse, {
    'courses endpoint returns HTTP 200': (res) => res.status === 200,
  });
  check(tracksResponse, {
    'tracks endpoint returns HTTP 200': (res) => res.status === 200,
  });
  check(coursesPayload, {
    'courses payload is valid': (body) => Boolean(body && body.success === true && Array.isArray(body.courses)),
  });
  check(tracksPayload, {
    'tracks payload is valid': (body) => Boolean(body && body.success === true && Array.isArray(body.tracks)),
  });

  sleep(1);
}
