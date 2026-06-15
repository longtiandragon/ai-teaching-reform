import Mock from 'mockjs';
import expertList from './ExpertList.json';

// 确保 idnum 是 number 类型，并赋初始值
let currentId = expertList.length;

Mock.mock('/api/ExpertList', 'get', {
  code: 200,
  message: 'success',
  data: expertList
});

// 新增
Mock.mock('/api/AddExpert', 'post', (options:any) => {
  const data = JSON.parse(options.body); // 解析请求体
  data.idnum = currentId++; // 自动生成唯一 idnum
  data.time = new Date().toLocaleString(); // 添加当前时间为发布时间
  expertList.push(data); // 将新数据添加到模拟的专家列表中
  return { code: 200 }; // 返回成功状态码
});


// 编辑
Mock.mock('/api/EditExpert', 'post', (options:any) => {
  const data = JSON.parse(options.body); // 解析请求体
  data.time = new Date().toLocaleString(); // 添加当前时间为发布时间
  const index = expertList.findIndex(i => i.idnum === data.idnum); // 查找要编辑的专家索引
  if (index > -1) {
    expertList.splice(index, 1, data); // 替换旧数据
  }
  return { code: 200 }; // 返回成功状态码
});


// 删除专家
Mock.mock('/api/DeleteExpert', 'post', (options: any) => {
  const { id } = JSON.parse(options.body);
  const index = expertList.findIndex(i => i.idnum === id);
  if (index > -1) {
    expertList.splice(index, 1); // 从列表中移除该项
  }
  return { code: 200 };
});



// 批量发布
Mock.mock('/api/BatchPublish', 'post', (options:any) => {
  const {ids} = JSON.parse(options.body); // 解析整个请求体,直接获取 ids 数组
  ids.forEach((id:number) => {
    const expert = expertList.find(e => e.idnum === id);
    if (expert) {
      expert.status = 1; // 更新状态为未发布
    }
  });

  return { code: 200};
});

// 批量推荐
Mock.mock('/api/BatchRecommend', 'post', (options:any) => {
  // const requestBody = JSON.parse(options.body); // 解析整个请求体
  // const ids = requestBody.ids; // 直接获取 ids 数组
  const {ids} = JSON.parse(options.body); // 解析整个请求体,直接获取 ids 数组
  ids.forEach((id:number) => {
    const expert = expertList.find(e => e.idnum === id);
    if (expert) {
      expert.isrecommand = 1; // 更新状态为不推荐
    }
  });

  return { code: 200};
});

// 批量取消发布
Mock.mock('/api/BatchUnPublish', 'post', (options:any) => {
  // const requestBody = JSON.parse(options.body); // 解析整个请求体
  // const ids = requestBody.ids; // 直接获取 ids 数组
  const {ids} = JSON.parse(options.body); // 解析整个请求体,直接获取 ids 数组
  ids.forEach((id:number) => {
    const expert = expertList.find(e => e.idnum === id);
    if (expert) {
      expert.status = 0; // 更新状态为未发布
    }
  });

  return { code: 200};
});

// 批量取消推荐
Mock.mock('/api/BatchUnRecommend', 'post', (options:any) => {
  // const requestBody = JSON.parse(options.body); // 解析整个请求体
  // const ids = requestBody.ids; // 直接获取 ids 数组
  const {ids} = JSON.parse(options.body); // 解析整个请求体,直接获取 ids 数组
  ids.forEach((id:number) => {
    const expert = expertList.find(e => e.idnum === id);
    if (expert) {
      expert.isrecommand = 0; // 更新状态为不推荐
    }
  });

  return { code: 200};
});

// Mock.mock('/api/BatchDelete', 'post', (options:any) => {
//   const { ids } = JSON.parse(options.body); // 获取请求体中的 id 列表

//   // 遍历 ids 数组，从 expertList 中移除对应的专家
//   ids.forEach((id:number) => {
//     const index = expertList.findIndex(expert => expert.idnum === id);
//     if (index !== -1) {
//       expertList.splice(index, 1); // 删除对应的专家记录
//     }
//   });

//   return { code: 200, message: '删除成功' };
// });