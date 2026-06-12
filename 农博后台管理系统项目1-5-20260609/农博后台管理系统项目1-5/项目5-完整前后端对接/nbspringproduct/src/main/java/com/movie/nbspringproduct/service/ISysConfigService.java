package com.movie.nbspringproduct.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.movie.nbspringproduct.entity.SysConfig;

import java.util.Map;

/**
 * 系统配置Service接口
 */
public interface ISysConfigService extends IService<SysConfig> {
    
    /**
     * 根据键名查询配置值
     * @param configKey 配置键名
     * @return 配置值
     */
    String getConfigValueByKey(String configKey);
    
    /**
     * 获取所有配置（以Map形式返回）
     * @return 配置Map
     */
    Map<String, String> getAllConfigMap();
    
    /**
     * 批量保存配置
     * @param configMap 配置Map
     */
    void saveConfigBatch(Map<String, String> configMap);
}

