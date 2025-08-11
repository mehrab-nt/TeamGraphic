export interface UserDto
{
    id: number
    full_name: string
}
export interface LoginDto {
    refresh: string
    access: string
    user: UserDto
}
