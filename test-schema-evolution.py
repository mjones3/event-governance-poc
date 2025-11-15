#!/usr/bin/env python3
import requests
import time
import random

ORDERS_SERVICE_URL = 'http://localhost:8080'
BLOOD_TYPES = ['A_POSITIVE', 'O_POSITIVE', 'B_POSITIVE', 'O_NEGATIVE', 'A_NEGATIVE', 'AB_POSITIVE']
PRIORITIES = ['ROUTINE', 'ROUTINE', 'URGENT', 'LIFE_THREATENING']
FACILITIES = [f'FAC-{i:03d}' for i in range(100, 150)]
ORDER_STATUSES = ['PENDING', 'APPROVED']
ORDER_SOURCES = ['WEB', 'MOBILE', 'API', 'INTERNAL']
NAMES = ['John Smith', 'Mary Jones', 'Bob Johnson', 'Alice Williams']

def create_v1_order():
    return {
        'orderId': f'ORD-V1-{random.randint(10000, 99999)}',
        'bloodType': random.choice(BLOOD_TYPES),
        'quantity': random.randint(1, 10),
        'priority': random.choice(PRIORITIES),
        'facilityId': random.choice(FACILITIES),
        'requestedBy': f'EMP{random.randint(1000, 9999)}',
        'orderStatus': random.choice(ORDER_STATUSES)
    }

def create_v2_order():
    order = {
        'orderId': f'ORD-V2-{random.randint(10000, 99999)}',
        'bloodType': random.choice(BLOOD_TYPES),
        'quantity': random.randint(1, 10),
        'priority': random.choice(PRIORITIES),
        'facilityId': random.choice(FACILITIES),
        'requestedBy': f'EMP{random.randint(1000, 9999)}',
        'orderStatus': random.choice(ORDER_STATUSES),
        'orderSource': random.choice(ORDER_SOURCES)
    }
    if random.random() < 0.8:
        order['requestedDeliveryDate'] = int((time.time() + random.randint(86400, 604800)) * 1000)
    if random.random() < 0.5:
        order['emergencyContact'] = {
            'name': random.choice(NAMES),
            'phone': f'+1-555-{random.randint(1000, 9999)}',
            'relationship': random.choice(['SPOUSE', 'PARENT', 'FRIEND'])
        }
    return order

print('=' * 70)
print('  BioPro Schema Evolution Test - 3000 Events')
print('  50/50 v1.0 and v2.0 split with variable data')
print('=' * 70)
print()

total_messages = 3000
messages_per_batch = 50
batch_delay = 1

print(f'Configuration:')
print(f'  Total messages: {total_messages}')
print(f'  Batch size: {messages_per_batch}')
print(f'  Batch delay: {batch_delay}s')
print(f'  v1/v2 split: 50/50 (target)')
print()
print('Starting test...')
print()

stats = {'v1.0': 0, 'v2.0': 0, 'failed': 0}
start_time = time.time()

for i in range(0, total_messages, messages_per_batch):
    batch_num = (i // messages_per_batch) + 1
    total_batches = total_messages // messages_per_batch
    
    print(f'[Batch {batch_num}/{total_batches}] Sending {messages_per_batch} messages...', end=' ')
    
    batch_stats = {'v1.0': 0, 'v2.0': 0}
    
    for j in range(messages_per_batch):
        if random.random() < 0.5:
            order, ver = create_v2_order(), 'v2.0'
        else:
            order, ver = create_v1_order(), 'v1.0'
        try:
            r = requests.post(f'{ORDERS_SERVICE_URL}/api/orders', json=order, timeout=5)
            if r.status_code == 200:
                stats[ver] += 1
                batch_stats[ver] += 1
            else:
                stats['failed'] += 1
        except:
            stats['failed'] += 1
        time.sleep(0.05)  # Faster for large batch
    
    v2_pct = (batch_stats['v2.0'] / messages_per_batch) * 100 if messages_per_batch > 0 else 0
    print(f'v1={batch_stats['v1.0']}, v2={batch_stats['v2.0']} ({v2_pct:.0f}% v2)')
    
    if batch_num % 10 == 0:
        elapsed = time.time() - start_time
        rate = (i + messages_per_batch) / elapsed
        print(f'  Progress: {i + messages_per_batch}/{total_messages} ({(i + messages_per_batch)/total_messages*100:.1f}%) | Rate: {rate:.1f} msg/s')
        print(f'  Cumulative: v1.0={stats['v1.0']}, v2.0={stats['v2.0']}, failed={stats['failed']}')
        print()
    
    if i + messages_per_batch < total_messages:
        time.sleep(batch_delay)

elapsed = time.time() - start_time
total_successful = stats['v1.0'] + stats['v2.0']

print()
print('=' * 70)
print('  Test Complete!')
print('=' * 70)
print()
print(f'Duration: {elapsed:.1f}s ({total_messages/elapsed:.1f} msg/s)')
print()
print('Final Statistics:')
if total_successful > 0:
    print(f'  v1.0: {stats['v1.0']} ({stats['v1.0']/total_successful*100:.1f}%)')
    print(f'  v2.0: {stats['v2.0']} ({stats['v2.0']/total_successful*100:.1f}%)')
else:
    print(f'  v1.0: {stats['v1.0']}')
    print(f'  v2.0: {stats['v2.0']}')
print(f'  Failed: {stats['failed']}')
print(f'  Total: {total_messages}')
print()

if stats['failed'] == 0:
    print('✅ All messages sent successfully!')
    print('✅ Check Grafana to visualize schema version distribution!')
else:
    print(f'⚠️  {stats['failed']} messages failed')
print()
