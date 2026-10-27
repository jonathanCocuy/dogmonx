import React, { useCallback, useEffect, useState } from 'react';
import { ActivityIndicator, FlatList, RefreshControl, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { ENDPOINTS } from '../../constants/api';
import { colors, fonts, radius } from '../../constants/theme';

interface Report {
  timestamp: string;
  description: string;
  dogs_count: number;
  motion_score: number;
}

function MotionDot({ score }: { score: number }) {
  const color = score < 0.1 ? colors.green : score < 0.3 ? colors.yellow : colors.red;
  return <View style={[dot.circle, { backgroundColor: color }]} />;
}
const dot = StyleSheet.create({
  circle: { width: 7, height: 7, borderRadius: 4 },
});

export default function HistoryScreen() {
  const { top } = useSafeAreaInsets();
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchHistory = useCallback(async () => {
    try {
      const res = await fetch(ENDPOINTS.history);
      const data = await res.json();
      setReports((data.reports ?? []).reverse());
    } catch {
      // silently fail
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => { fetchHistory(); }, [fetchHistory]);

  const timeStr = (ts: string) =>
    new Date(ts).toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' });

  return (
    <View style={[styles.container, { paddingTop: top + 16 }]}>
      <Text style={styles.title}>Historial</Text>
      {loading ? (
        <ActivityIndicator color={colors.textSecondary} style={{ marginTop: 40 }} />
      ) : (
        <FlatList
          data={reports}
          keyExtractor={(item) => item.timestamp}
          contentContainerStyle={{ paddingBottom: 20 }}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={() => { setRefreshing(true); fetchHistory(); }}
              tintColor={colors.textTertiary}
            />
          }
          ItemSeparatorComponent={() => <View style={styles.separator} />}
          ListEmptyComponent={
            <Text style={styles.empty}>Sin reportes por ahora.</Text>
          }
          renderItem={({ item }) => (
            <View style={styles.item}>
              <View style={styles.itemLeft}>
                <MotionDot score={item.motion_score} />
                <Text style={styles.time}>{timeStr(item.timestamp)}</Text>
              </View>
              <View style={styles.itemRight}>
                <Text style={styles.desc}>{item.description}</Text>
                <Text style={styles.dogs}>
                  {'🐕'.repeat(Math.min(item.dogs_count, 4)) || '—'}
                </Text>
              </View>
            </View>
          )}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg, paddingHorizontal: 20, paddingBottom: 120 },
  title: { fontFamily: fonts.jakartaBold, fontSize: 28, color: colors.text, letterSpacing: -0.5, marginBottom: 20 },
  item: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 14,
    paddingVertical: 14,
  },
  itemLeft: {
    alignItems: 'center',
    gap: 6,
    paddingTop: 4,
    width: 48,
  },
  time: {
    fontFamily: fonts.medium,
    fontSize: 11,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  itemRight: {
    flex: 1,
  },
  desc: {
    fontFamily: fonts.regular,
    fontSize: 14,
    color: colors.text,
    lineHeight: 22,
  },
  dogs: {
    fontSize: 14,
    marginTop: 4,
  },
  separator: {
    height: 1,
    backgroundColor: colors.border,
    marginLeft: 62,
  },
  empty: {
    fontFamily: fonts.regular,
    fontSize: 14,
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: 60,
  },
});
