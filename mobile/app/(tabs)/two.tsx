import React, { useCallback, useEffect, useState } from 'react';
import { ActivityIndicator, RefreshControl, ScrollView, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { ENDPOINTS } from '../../constants/api';
import { colors, fonts, radius } from '../../constants/theme';

interface Report {
  timestamp: string;
  description: string;
  dogs_count: number;
  motion_score: number;
}

function MotionBar({ score }: { score: number }) {
  const pct = Math.min(score * 100, 100);
  const color = score < 0.1 ? colors.green : score < 0.3 ? colors.yellow : colors.red;
  return (
    <View style={bar.track}>
      <View style={[bar.fill, { width: `${pct}%` as any, backgroundColor: color }]} />
    </View>
  );
}
const bar = StyleSheet.create({
  track: { height: 3, backgroundColor: colors.surfaceHigh, borderRadius: 2, overflow: 'hidden', flex: 1 },
  fill: { height: '100%', borderRadius: 2 },
});

export default function ReportScreen() {
  const { top } = useSafeAreaInsets();
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(false);

  const fetchReport = useCallback(async () => {
    try {
      const res = await fetch(ENDPOINTS.latestReport);
      const data = await res.json();
      if (data.timestamp) { setReport(data); setError(false); }
    } catch { setError(true); }
    finally { setLoading(false); setRefreshing(false); }
  }, []);

  useEffect(() => {
    fetchReport();
    const id = setInterval(fetchReport, 10_000);
    return () => clearInterval(id);
  }, [fetchReport]);

  const motionLabel = (score: number) => {
    if (score < 0.1) return { label: 'Quietos', color: colors.green };
    if (score < 0.3) return { label: 'Activos', color: colors.yellow };
    return { label: 'Muy activos', color: colors.red };
  };

  const timeStr = report
    ? new Date(report.timestamp).toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' })
    : '';

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={[styles.content, { paddingTop: top + 16 }]}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); fetchReport(); }} tintColor={colors.textTertiary} />
      }
    >
      <Text style={styles.title}>Reporte</Text>

      {loading ? (
        <View style={styles.loadingBox}>
          <ActivityIndicator color={colors.textSecondary} />
        </View>
      ) : error ? (
        <View style={styles.card}>
          <Text style={styles.errorText}>Sin conexión al backend</Text>
        </View>
      ) : report ? (
        <>
          <View style={styles.card}>
            <Text style={styles.description}>{report.description}</Text>
            <View style={styles.divider} />

            <View style={styles.row}>
              <Text style={styles.metaLabel}>Perros</Text>
              <Text style={styles.metaValue}>{'🐕'.repeat(Math.min(report.dogs_count, 4)) || '—'}</Text>
            </View>

            <View style={[styles.row, { marginTop: 10 }]}>
              <Text style={styles.metaLabel}>Actividad</Text>
              <View style={styles.motionRow}>
                <MotionBar score={report.motion_score} />
                <Text style={[styles.motionLabel, { color: motionLabel(report.motion_score).color }]}>
                  {motionLabel(report.motion_score).label}
                </Text>
              </View>
            </View>
          </View>

          <Text style={styles.timestamp}>Última actualización · {timeStr}</Text>
        </>
      ) : (
        <View style={styles.card}>
          <Text style={styles.emptyText}>Esperando primer reporte…</Text>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  content: { padding: 20, paddingTop: 0, paddingBottom: 120 },
  title: { fontFamily: fonts.jakartaBold, fontSize: 28, color: colors.text, letterSpacing: -0.5, marginBottom: 20 },
  loadingBox: { alignItems: 'center', paddingTop: 60 },
  card: {
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    padding: 20,
    borderWidth: 1,
    borderColor: colors.border,
  },
  description: {
    fontFamily: fonts.regular,
    fontSize: 16,
    color: colors.text,
    lineHeight: 26,
  },
  divider: { height: 1, backgroundColor: colors.border, marginVertical: 16 },
  row: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  metaLabel: { fontFamily: fonts.medium, fontSize: 13, color: colors.textSecondary },
  metaValue: { fontSize: 18 },
  motionRow: { flexDirection: 'row', alignItems: 'center', gap: 10, flex: 1, marginLeft: 16 },
  motionLabel: { fontFamily: fonts.medium, fontSize: 13 },
  timestamp: {
    fontFamily: fonts.regular,
    fontSize: 12,
    color: colors.textTertiary,
    textAlign: 'center',
    marginTop: 14,
  },
  emptyText: { fontFamily: fonts.regular, fontSize: 14, color: colors.textSecondary, textAlign: 'center', paddingVertical: 20 },
  errorText: { fontFamily: fonts.regular, fontSize: 14, color: colors.red, textAlign: 'center', paddingVertical: 20 },
});
