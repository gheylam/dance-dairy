-- Seed fixtures shaped by live BookWhen probe (DGC + LUM3X verified, KMDC same shell).
-- Idempotent for classes/studios; scrape_runs appends one audit row per studio per run.

INSERT INTO studios (slug, canonical_name, listing_url, booking_system, scrape_permission, timezone) VALUES
  ('dgcdance','DGC Dance','https://bookwhen.com/dgcdance?tag=Class','bookwhen',true,'Europe/London'),
  ('lum3x','LUM3X','https://bookwhen.com/lum3x','bookwhen',true,'Europe/London'),
  ('kpopinlondonmin','KMDC','https://bookwhen.com/kpopinlondonmin','bookwhen',true,'Europe/London')
ON CONFLICT (slug) DO UPDATE SET
  canonical_name=EXCLUDED.canonical_name, listing_url=EXCLUDED.listing_url;

INSERT INTO scrape_runs (studio_slug, started_at, finished_at, status, rows_fetched) VALUES
  ('dgcdance',now(),now(),'ok',1),
  ('lum3x',now(),now(),'ok',3),
  ('kpopinlondonmin',now(),now(),'ok',1);

-- DGC: teacher via tag-join, section Highlight, £18 single
INSERT INTO classes (studio_slug,source_id,event_group_id,status,studio_raw,teacher,teacher_confidence,
  song,artist,difficulty,song_section,start_at,end_at,venue,address,area,
  price_pence,price_currency,price_raw,price_tier,booking_url,source_url,title_raw,tags,scrape_run_id) VALUES
  ('dgcdance','ev-s3wew-20260925183000',NULL,'scheduled','DGC Dance','Caroline','tag-join',
   'ON','BTS','All Levels','Highlight','2026-09-25 18:30:00+01','2026-09-25 20:30:00+01',
   'Ironmonger Row Baths','Ironmonger Row, London EC1V 3QN','Islington',
   1800,'GBP','£18.00 (inc VAT)','single','https://bookwhen.com/dgcdance/e/ev-s3wew-20260925183000',
   'https://bookwhen.com/dgcdance/e/ev-s3wew-20260925183000','BTS - ON (Highlight)','{Highlight,Caroline}',
   (SELECT max(id) FROM scrape_runs WHERE studio_slug='dgcdance'))
ON CONFLICT (studio_slug, source_id, start_at) DO UPDATE SET
  teacher=EXCLUDED.teacher, song=EXCLUDED.song, artist=EXCLUDED.artist, updated_at=now(), scraped_at=now();

-- LUM3X song: teacher in title, section Last Chorus, £15 single
INSERT INTO classes (studio_slug,source_id,event_group_id,status,studio_raw,teacher,teacher_confidence,
  song,artist,difficulty,song_section,start_at,end_at,venue,address,area,
  price_pence,price_currency,price_raw,price_tier,booking_url,source_url,title_raw,tags,scrape_run_id) VALUES
  ('lum3x','ev-sbpdr-20260929193000',NULL,'scheduled','LUM3X','Sophia','title',
   'SaWaDiKa','LISA','All Levels','Last Chorus','2026-09-29 19:30:00+01','2026-09-29 21:00:00+01',
   'Pancras Square Leisure','5 Pancras Sq, London N1C 4AG','Kings Cross',
   1500,'GBP','£15.00','single','https://bookwhen.com/lum3x/e/ev-sbpdr-20260929193000',
   'https://bookwhen.com/lum3x/e/ev-sbpdr-20260929193000','LISA - ''SaWaDiKa'' (Sophia Choreography) [All Levels]','{All Levels}',
   (SELECT max(id) FROM scrape_runs WHERE studio_slug='lum3x'))
ON CONFLICT (studio_slug, source_id, start_at) DO UPDATE SET
  teacher=EXCLUDED.teacher, song=EXCLUDED.song, artist=EXCLUDED.artist, updated_at=now(), scraped_at=now();

-- LUM3X course: one group id, two occurrence rows, price_tier course
INSERT INTO classes (studio_slug,source_id,event_group_id,status,studio_raw,teacher,teacher_confidence,
  song,artist,difficulty,song_section,start_at,end_at,venue,address,area,
  price_pence,price_currency,price_raw,price_tier,booking_url,source_url,title_raw,tags,scrape_run_id) VALUES
  ('lum3x','ev-sd5k0-20260928193000','ev-sd5k0-20260928193000','scheduled','LUM3X',NULL,'unknown',
   NULL,NULL,'Beginners',NULL,'2026-09-28 19:30:00+01','2026-09-28 21:00:00+01',
   'The Marshall Building','44 Lincoln''s Inn Fields, London WC2A 3ED','Holborn',
   3000,'GBP','£30.00 (2 dates)','course','https://bookwhen.com/lum3x/e/ev-sd5k0-20260928193000',
   'https://bookwhen.com/lum3x/e/ev-sd5k0-20260928193000','Find Your Fundamentals: Training Course [Beg/Int]','{Course,Beginners}',
   (SELECT max(id) FROM scrape_runs WHERE studio_slug='lum3x')),
  ('lum3x','ev-sd5k0-20260928193000','ev-sd5k0-20260928193000','scheduled','LUM3X',NULL,'unknown',
   NULL,NULL,'Beginners',NULL,'2026-10-05 19:30:00+01','2026-10-05 21:00:00+01',
   'The Marshall Building','44 Lincoln''s Inn Fields, London WC2A 3ED','Holborn',
   3000,'GBP','£30.00 (2 dates)','course','https://bookwhen.com/lum3x/e/ev-sd5k0-20260928193000',
   'https://bookwhen.com/lum3x/e/ev-sd5k0-20260928193000','Find Your Fundamentals: Training Course [Beg/Int]','{Course,Beginners}',
   (SELECT max(id) FROM scrape_runs WHERE studio_slug='lum3x'))
ON CONFLICT (studio_slug, source_id, start_at) DO UPDATE SET
  updated_at=now(), scraped_at=now();

-- KMDC: same shell, teacher unknown until tag-join spike lands
INSERT INTO classes (studio_slug,source_id,event_group_id,status,studio_raw,teacher,teacher_confidence,
  song,artist,difficulty,song_section,start_at,end_at,venue,address,area,
  price_pence,price_currency,price_raw,price_tier,booking_url,source_url,title_raw,tags,scrape_run_id) VALUES
  ('kpopinlondonmin','ev-kmdc-sample01',NULL,'scheduled','KMDC',NULL,'unknown',
   'MONEY','LISA','All Levels',NULL,'2026-10-07 18:00:00+01','2026-10-07 19:30:00+01',
   'The Marshall Building','44 Lincoln''s Inn Fields, London WC2A 3ED','Holborn',
   1500,'GBP','£15.00','single','https://bookwhen.com/kpopinlondonmin/e/ev-kmdc-sample01',
   'https://bookwhen.com/kpopinlondonmin/e/ev-kmdc-sample01','【All Levels】MONEY - LISA (1.5h)','{All Levels}',
   (SELECT max(id) FROM scrape_runs WHERE studio_slug='kpopinlondonmin'))
ON CONFLICT (studio_slug, source_id, start_at) DO UPDATE SET
  teacher=EXCLUDED.teacher, song=EXCLUDED.song, artist=EXCLUDED.artist, updated_at=now(), scraped_at=now();
