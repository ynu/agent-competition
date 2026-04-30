import request from '@/utils/request'

/**
 * @description 个人中心—用户信息
 */
export function myuserinfo() {
  return request.get('/api/v1/user/myuserinfo')
}
