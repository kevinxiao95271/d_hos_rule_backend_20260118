/**
 * Cross规则API TypeScript接口定义
 * 
 * 使用方式:
 * 1. 将此文件复制到你的项目中
 * 2. 根据需要调整命名空间和导出方式
 * 3. 在API调用中使用这些类型定义
 * 
 * @version 1.0.0
 * @date 2026-01-19
 */

// ==================== 基础类型定义 ====================

/**
 * API通用响应结构
 */
export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

/**
 * Cross规则违规详情
 */
export interface CrossDefect {
  /** 规则代码 */
  ruleCode: string;
  /** 规则描述 */
  ruleDescription: string;
  /** Cross规则类型 */
  crossType: 'field_pair' | 'age_gender' | 'conditional_required' | 'age_diagnosis' | 'transfusion_logic' | 'date_consistency' | 'logic_check';
  /** 涉及的字段列表 */
  involvedFields: string[];
  /** 字段值映射 */
  fieldValues?: Record<string, string>;
  /** 逻辑描述 */
  logicDescription?: string;
  /** 扣分 */
  deductScore: number;
  /** 严重程度 */
  severity: 'low' | 'medium' | 'high';
}

/**
 * 普通违规详情
 */
export interface DefectDetail {
  /** 字段代码 */
  fieldCode: string;
  /** 字段名称 */
  fieldName: string;
  /** 规则代码 */
  ruleCode: string;
  /** 规则描述 */
  ruleDescription: string;
  /** 实际值 */
  actualValue: string;
  /** 期望值 */
  expectedValue: string;
  /** 扣分 */
  deductScore: number;
}

// ==================== 单病案质控API ====================

/**
 * 单病案质控请求参数
 */
export interface SingleQcRequest {
  /** 病案号 */
  a48: string;
  /** 住院次数 */
  a49: string;
}

/**
 * 单病案质控响应数据
 * 🆕 新增了Cross规则统计字段
 */
export interface SingleQcResult {
  /** 病案键 */
  mrKey: string;
  /** 病案号 */
  a48: string;
  /** 住院次数 */
  a49: string;
  /** 出院日期 */
  b15?: string;
  
  // === 基础统计（原有字段） ===
  /** 总违规数 */
  defectCount: number;
  /** 总扣分 */
  totalDeduct: number;
  /** 最终得分 */
  finalScore: number;
  
  // === 违规详情（原有字段） ===
  /** 所有违规详情 */
  allDefects: DefectDetail[];
  /** 按字段分组的违规（不包含Cross规则） */
  defectsByField: Record<string, DefectDetail[]>;
  /** Cross规则违规详情 */
  crossDefects: CrossDefect[];
  
  // === 🆕 新增：Cross规则统计字段 ===
  /** Cross规则违规总数 */
  crossDefectCount: number;
  /** Cross规则总扣分 */
  crossTotalDeduct: number;
}

/**
 * 单病案质控API响应
 */
export type SingleQcResponse = ApiResponse<SingleQcResult>;

// ==================== 批量质控API ====================

/**
 * 批量质控请求参数
 */
export interface BatchQcRequest {
  /** 时间类型 */
  periodType: 'year' | 'quarter' | 'month';
  /** 年份 */
  year: number;
  /** 季度（可选） */
  quarter?: number;
  /** 月份（可选） */
  month?: number;
}

/**
 * 批量质控响应数据
 * 🆕 新增了Cross规则统计字段
 */
export interface BatchQcResult {
  /** 批次键 */
  batchKey: string;
  /** 时间类型 */
  periodType: string;
  /** 年份 */
  year: number;
  /** 季度 */
  quarter?: number;
  /** 月份 */
  month?: number;
  
  // === 基础统计（原有字段） ===
  /** 病案数量 */
  caseCount: number;
  /** 总违规数 */
  totalDefectCount: number;
  /** 平均违规数 */
  avgDefect: number;
  /** 平均得分 */
  avgScore: number;
  
  // === 状态信息（原有字段） ===
  /** 状态 */
  status: 'processing' | 'completed' | 'failed';
  /** 进度百分比 */
  progress: number;
  /** 开始时间 */
  startTime?: string;
  /** 结束时间 */
  endTime?: string;
  /** 已执行时间（秒） */
  elapsedSeconds?: number;
  
  // === 🆕 新增：Cross规则统计字段 ===
  /** Cross规则违规总数 */
  crossDefectCount: number;
  /** Cross规则总扣分 */
  crossTotalDeduct: number;
  /** 平均Cross规则违规数 */
  avgCrossDefect: number;
}

/**
 * 批量质控API响应
 */
export type BatchQcResponse = ApiResponse<BatchQcResult>;

// ==================== 工具类型和函数 ====================

/**
 * Cross规则统计信息
 */
export interface CrossRuleStats {
  /** 违规数量 */
  count: number;
  /** 总扣分 */
  totalDeduct: number;
  /** 占总违规的比例（百分比） */
  ratio: number;
}

/**
 * 计算Cross规则统计
 */
export function calculateCrossStats(data: SingleQcResult): CrossRuleStats {
  const ratio = data.defectCount > 0 
    ? (data.crossDefectCount / data.defectCount) * 100 
    : 0;
    
  return {
    count: data.crossDefectCount,
    totalDeduct: data.crossTotalDeduct,
    ratio: Math.round(ratio * 10) / 10 // 保留1位小数
  };
}

/**
 * 计算批量Cross规则统计
 */
export function calculateBatchCrossStats(data: BatchQcResult): CrossRuleStats {
  const ratio = data.totalDefectCount > 0 
    ? (data.crossDefectCount / data.totalDefectCount) * 100 
    : 0;
    
  return {
    count: data.crossDefectCount,
    totalDeduct: data.crossTotalDeduct,
    ratio: Math.round(ratio * 10) / 10
  };
}

/**
 * 验证Cross规则数据一致性
 */
export function validateCrossRuleData(data: SingleQcResult): boolean {
  // 检查Cross违规数量一致性
  if (data.crossDefectCount !== data.crossDefects.length) {
    console.warn(`Cross违规数量不一致: count=${data.crossDefectCount}, details=${data.crossDefects.length}`);
    return false;
  }
  
  // 检查总违规数量逻辑
  const normalDefects = data.allDefects.filter(d => !d.ruleCode.startsWith('RULE_CROSS_')).length;
  if (data.defectCount !== normalDefects + data.crossDefectCount) {
    console.warn('总违规数量计算错误');
    return false;
  }
  
  return true;
}

/**
 * 安全获取Cross规则数据（处理字段缺失）
 */
export function safeCrossRuleData<T extends Partial<SingleQcResult>>(data: T): T & Required<Pick<SingleQcResult, 'crossDefectCount' | 'crossTotalDeduct' | 'crossDefects'>> {
  return {
    ...data,
    crossDefectCount: data.crossDefectCount ?? 0,
    crossTotalDeduct: data.crossTotalDeduct ?? 0,
    crossDefects: data.crossDefects ?? []
  };
}

/**
 * 安全获取批量Cross规则数据
 */
export function safeBatchCrossRuleData<T extends Partial<BatchQcResult>>(data: T): T & Required<Pick<BatchQcResult, 'crossDefectCount' | 'crossTotalDeduct' | 'avgCrossDefect'>> {
  return {
    ...data,
    crossDefectCount: data.crossDefectCount ?? 0,
    crossTotalDeduct: data.crossTotalDeduct ?? 0,
    avgCrossDefect: data.avgCrossDefect ?? 0
  };
}

// ==================== React Hook示例 ====================

/**
 * React Hook示例：使用Cross规则统计
 * 
 * 使用方式：
 * ```tsx
 * const { crossStats, isLoading, error } = useCrossRuleStats(qcResult);
 * ```
 */
export interface UseCrossRuleStatsResult {
  crossStats: CrossRuleStats;
  isValid: boolean;
  hasViolations: boolean;
}

// 注意：这只是类型定义示例，实际Hook实现需要在React项目中完成
export type UseCrossRuleStatsHook = (data: SingleQcResult | null) => UseCrossRuleStatsResult;

// ==================== 常量定义 ====================

/**
 * Cross规则类型映射
 */
export const CROSS_RULE_TYPE_LABELS: Record<CrossDefect['crossType'], string> = {
  field_pair: '字段配对检查',
  age_gender: '年龄性别逻辑',
  conditional_required: '条件必填检查',
  age_diagnosis: '年龄诊断匹配',
  transfusion_logic: '输血逻辑检查',
  date_consistency: '日期一致性检查',
  logic_check: '逻辑检查'
};

/**
 * 严重程度映射
 */
export const SEVERITY_LABELS: Record<CrossDefect['severity'], string> = {
  low: '轻微',
  medium: '中等',
  high: '严重'
};

/**
 * 严重程度颜色映射（用于UI展示）
 */
export const SEVERITY_COLORS: Record<CrossDefect['severity'], string> = {
  low: '#4caf50',    // 绿色
  medium: '#ff9800', // 橙色
  high: '#f44336'    // 红色
};

// ==================== 导出所有类型 ====================

export type {
  // 基础类型
  ApiResponse,
  CrossDefect,
  DefectDetail,
  
  // 单病案质控
  SingleQcRequest,
  SingleQcResult,
  SingleQcResponse,
  
  // 批量质控
  BatchQcRequest,
  BatchQcResult,
  BatchQcResponse,
  
  // 工具类型
  CrossRuleStats,
  UseCrossRuleStatsResult,
  UseCrossRuleStatsHook
};

export {
  // 工具函数
  calculateCrossStats,
  calculateBatchCrossStats,
  validateCrossRuleData,
  safeCrossRuleData,
  safeBatchCrossRuleData,
  
  // 常量
  CROSS_RULE_TYPE_LABELS,
  SEVERITY_LABELS,
  SEVERITY_COLORS
};