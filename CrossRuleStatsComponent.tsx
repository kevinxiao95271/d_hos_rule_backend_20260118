/**
 * Cross规则统计组件示例
 * 
 * 这个组件展示了如何在React项目中集成Cross规则统计功能
 * 
 * 使用方式：
 * ```tsx
 * <CrossRuleStatsCard data={qcResult} />
 * <BatchCrossRuleStats data={batchResult} />
 * ```
 */

import React from 'react';
import { 
  SingleQcResult, 
  BatchQcResult, 
  CrossDefect,
  calculateCrossStats,
  calculateBatchCrossStats,
  validateCrossRuleData,
  CROSS_RULE_TYPE_LABELS,
  SEVERITY_COLORS
} from './cross-rules-api-types';

// ==================== 样式定义 ====================

const styles = {
  card: {
    border: '1px solid #e1f5fe',
    borderRadius: '8px',
    background: 'linear-gradient(135deg, #f3e5f5 0%, #e8f5e8 100%)',
    padding: '16px',
    margin: '16px 0',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '16px'
  },
  title: {
    margin: 0,
    color: '#1976d2',
    fontSize: '18px'
  },
  badge: {
    background: '#4caf50',
    color: 'white',
    padding: '4px 12px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: 'bold'
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
    gap: '16px',
    marginBottom: '16px'
  },
  statItem: {
    textAlign: 'center' as const,
    padding: '12px',
    background: 'rgba(255,255,255,0.7)',
    borderRadius: '6px'
  },
  statLabel: {
    display: 'block',
    fontSize: '12px',
    color: '#666',
    marginBottom: '4px'
  },
  statValue: {
    display: 'block',
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#1976d2'
  },
  crossCount: {
    color: '#ff6b35'
  },
  crossDeduct: {
    color: '#d32f2f'
  },
  crossRatio: {
    color: '#1976d2'
  },
  defectsList: {
    marginTop: '16px'
  },
  defectItem: {
    background: 'rgba(255,255,255,0.8)',
    border: '1px solid #ddd',
    borderRadius: '6px',
    padding: '12px',
    marginBottom: '8px'
  },
  defectHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '8px'
  },
  ruleCode: {
    fontFamily: 'monospace',
    fontSize: '12px',
    background: '#f5f5f5',
    padding: '2px 6px',
    borderRadius: '3px'
  },
  severityBadge: {
    padding: '2px 8px',
    borderRadius: '10px',
    fontSize: '11px',
    color: 'white',
    fontWeight: 'bold'
  },
  description: {
    color: '#333',
    fontSize: '14px',
    marginBottom: '4px'
  },
  typeLabel: {
    color: '#666',
    fontSize: '12px'
  },
  noData: {
    textAlign: 'center' as const,
    color: '#999',
    padding: '20px',
    fontStyle: 'italic'
  },
  warning: {
    background: '#fff3cd',
    border: '1px solid #ffeaa7',
    borderRadius: '4px',
    padding: '8px 12px',
    marginBottom: '16px',
    color: '#856404'
  }
};

// ==================== 单病案Cross规则统计卡片 ====================

interface CrossRuleStatsCardProps {
  data: SingleQcResult;
  showDetails?: boolean;
}

export const CrossRuleStatsCard: React.FC<CrossRuleStatsCardProps> = ({ 
  data, 
  showDetails = true 
}) => {
  // 数据验证
  const isValid = validateCrossRuleData(data);
  const crossStats = calculateCrossStats(data);
  
  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <h3 style={styles.title}>🎯 Cross规则统计</h3>
        <span style={styles.badge}>跨字段检查</span>
      </div>
      
      {!isValid && (
        <div style={styles.warning}>
          ⚠️ 数据一致性检查失败，请检查API响应
        </div>
      )}
      
      <div style={styles.statsGrid}>
        <div style={styles.statItem}>
          <span style={styles.statLabel}>违规数量</span>
          <span style={{...styles.statValue, ...styles.crossCount}}>
            {crossStats.count}
          </span>
        </div>
        
        <div style={styles.statItem}>
          <span style={styles.statLabel}>扣分总计</span>
          <span style={{...styles.statValue, ...styles.crossDeduct}}>
            {crossStats.totalDeduct.toFixed(1)}
          </span>
        </div>
        
        <div style={styles.statItem}>
          <span style={styles.statLabel}>占比</span>
          <span style={{...styles.statValue, ...styles.crossRatio}}>
            {crossStats.ratio}%
          </span>
        </div>
      </div>
      
      {showDetails && crossStats.count > 0 && (
        <CrossDefectsList defects={data.crossDefects} />
      )}
      
      {crossStats.count === 0 && (
        <div style={styles.noData}>
          ✅ 未发现Cross规则违规
        </div>
      )}
    </div>
  );
};

// ==================== Cross规则违规详情列表 ====================

interface CrossDefectsListProps {
  defects: CrossDefect[];
  maxItems?: number;
}

const CrossDefectsList: React.FC<CrossDefectsListProps> = ({ 
  defects, 
  maxItems = 5 
}) => {
  const displayDefects = defects.slice(0, maxItems);
  const hasMore = defects.length > maxItems;
  
  return (
    <div style={styles.defectsList}>
      <h4 style={{ margin: '0 0 12px 0', fontSize: '14px', color: '#666' }}>
        违规详情 ({defects.length}项)
      </h4>
      
      {displayDefects.map((defect, index) => (
        <div key={index} style={styles.defectItem}>
          <div style={styles.defectHeader}>
            <span style={styles.ruleCode}>{defect.ruleCode}</span>
            <span 
              style={{
                ...styles.severityBadge,
                backgroundColor: SEVERITY_COLORS[defect.severity]
              }}
            >
              {defect.severity}
            </span>
          </div>
          
          <div style={styles.description}>
            {defect.ruleDescription}
          </div>
          
          <div style={styles.typeLabel}>
            类型: {CROSS_RULE_TYPE_LABELS[defect.crossType]}
          </div>
          
          {defect.involvedFields && defect.involvedFields.length > 0 && (
            <div style={styles.typeLabel}>
              涉及字段: {defect.involvedFields.join(', ')}
            </div>
          )}
        </div>
      ))}
      
      {hasMore && (
        <div style={styles.noData}>
          还有 {defects.length - maxItems} 项违规...
        </div>
      )}
    </div>
  );
};

// ==================== 批量质控Cross规则统计 ====================

interface BatchCrossRuleStatsProps {
  data: BatchQcResult;
}

export const BatchCrossRuleStats: React.FC<BatchCrossRuleStatsProps> = ({ data }) => {
  const crossStats = calculateBatchCrossStats(data);
  
  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <h3 style={styles.title}>📊 批量Cross规则统计</h3>
        <span style={styles.badge}>{data.batchKey}</span>
      </div>
      
      <div style={styles.statsGrid}>
        <div style={styles.statItem}>
          <span style={styles.statLabel}>处理病案</span>
          <span style={styles.statValue}>
            {data.caseCount}
          </span>
        </div>
        
        <div style={styles.statItem}>
          <span style={styles.statLabel}>Cross违规总数</span>
          <span style={{...styles.statValue, ...styles.crossCount}}>
            {crossStats.count}
          </span>
        </div>
        
        <div style={styles.statItem}>
          <span style={styles.statLabel}>Cross总扣分</span>
          <span style={{...styles.statValue, ...styles.crossDeduct}}>
            {crossStats.totalDeduct.toFixed(1)}
          </span>
        </div>
        
        <div style={styles.statItem}>
          <span style={styles.statLabel}>平均Cross违规</span>
          <span style={styles.statValue}>
            {data.avgCrossDefect.toFixed(2)}
          </span>
        </div>
        
        <div style={styles.statItem}>
          <span style={styles.statLabel}>Cross占比</span>
          <span style={{...styles.statValue, ...styles.crossRatio}}>
            {crossStats.ratio}%
          </span>
        </div>
      </div>
      
      {/* 进度条 */}
      {data.status === 'processing' && (
        <div style={{ marginTop: '16px' }}>
          <div style={{ 
            background: '#f0f0f0', 
            borderRadius: '10px', 
            height: '8px',
            overflow: 'hidden'
          }}>
            <div style={{
              background: '#4caf50',
              height: '100%',
              width: `${data.progress}%`,
              transition: 'width 0.3s ease'
            }} />
          </div>
          <div style={{ 
            textAlign: 'center', 
            marginTop: '8px', 
            fontSize: '12px', 
            color: '#666' 
          }}>
            进度: {data.progress}%
          </div>
        </div>
      )}
    </div>
  );
};

// ==================== 对比统计组件 ====================

interface CrossRuleComparisonProps {
  data: SingleQcResult;
}

export const CrossRuleComparison: React.FC<CrossRuleComparisonProps> = ({ data }) => {
  const crossStats = calculateCrossStats(data);
  const normalDefects = data.defectCount - data.crossDefectCount;
  const normalDeduct = data.totalDeduct - data.crossTotalDeduct;
  
  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <h3 style={styles.title}>⚖️ 规则类型对比</h3>
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        {/* 普通规则 */}
        <div style={{
          ...styles.statItem,
          background: 'rgba(54, 162, 235, 0.1)',
          border: '2px solid rgba(54, 162, 235, 0.3)'
        }}>
          <h4 style={{ margin: '0 0 12px 0', color: '#36a2eb' }}>普通规则</h4>
          <div style={{ marginBottom: '8px' }}>
            <span style={styles.statLabel}>违规数</span>
            <span style={{ ...styles.statValue, color: '#36a2eb' }}>
              {normalDefects}
            </span>
          </div>
          <div>
            <span style={styles.statLabel}>扣分</span>
            <span style={{ ...styles.statValue, color: '#36a2eb' }}>
              {normalDeduct.toFixed(1)}
            </span>
          </div>
        </div>
        
        {/* Cross规则 */}
        <div style={{
          ...styles.statItem,
          background: 'rgba(255, 107, 53, 0.1)',
          border: '2px solid rgba(255, 107, 53, 0.3)'
        }}>
          <h4 style={{ margin: '0 0 12px 0', color: '#ff6b35' }}>Cross规则</h4>
          <div style={{ marginBottom: '8px' }}>
            <span style={styles.statLabel}>违规数</span>
            <span style={{ ...styles.statValue, color: '#ff6b35' }}>
              {crossStats.count}
            </span>
          </div>
          <div>
            <span style={styles.statLabel}>扣分</span>
            <span style={{ ...styles.statValue, color: '#ff6b35' }}>
              {crossStats.totalDeduct.toFixed(1)}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

// ==================== Hook示例 ====================

/**
 * 自定义Hook：处理Cross规则统计
 */
export const useCrossRuleStats = (data: SingleQcResult | null) => {
  if (!data) {
    return {
      crossStats: { count: 0, totalDeduct: 0, ratio: 0 },
      isValid: false,
      hasViolations: false
    };
  }
  
  const crossStats = calculateCrossStats(data);
  const isValid = validateCrossRuleData(data);
  const hasViolations = crossStats.count > 0;
  
  return {
    crossStats,
    isValid,
    hasViolations
  };
};

// ==================== 导出组件 ====================

export default {
  CrossRuleStatsCard,
  BatchCrossRuleStats,
  CrossRuleComparison,
  CrossDefectsList,
  useCrossRuleStats
};